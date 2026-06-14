"""
GroomX v6 - Home Visit Routes
GET    /api/home-visits/        - list home visits
POST   /api/home-visits/        - create home visit booking
GET    /api/home-visits/<id>    - get single visit
PATCH  /api/home-visits/<id>    - update status
DELETE /api/home-visits/<id>    - cancel
"""

from flask import Blueprint, request
from config.database import get_db
from utils import generate_visit_id, serialize, serialize_list, calc_travel_fee, ok, err, require_auth
from config.settings import Config
from datetime import datetime

home_visits_bp = Blueprint("home_visits", __name__)


# ── List ─────────────────────────────────────────────────────────────────────

@home_visits_bp.route("/", methods=["GET"])
@require_auth
def list_visits():
    db    = get_db()
    query = {}

    status = request.args.get("status")
    date   = request.args.get("date")

    if status:
        query["status"] = status
    if date:
        query["date"] = date
    if request.user.get("role") == "customer":
        query["user_id"] = request.user["sub"]

    docs = list(db.home_visits.find(query).sort("created_at", -1))
    return ok(serialize_list(docs))


# ── Create ────────────────────────────────────────────────────────────────────

@home_visits_bp.route("/", methods=["POST"])
@require_auth
def create_visit():
    data        = request.get_json() or {}
    name        = data.get("name", "").strip()
    phone       = data.get("phone", "").strip()
    service     = data.get("service", "").strip()
    address     = data.get("address", "").strip()
    landmark    = data.get("landmark", "")
    date        = data.get("date", "").strip()
    time        = data.get("time", "").strip()
    distance_km = float(data.get("distance_km", 5))

    # Validation
    if not all([name, phone, service, address, date, time]):
        return err("name, phone, service, address, date, time are all required")

    if service not in Config.SERVICES:
        return err(f"Unknown service. Valid: {list(Config.SERVICES.keys())}")

    if distance_km > Config.HOME_VISIT_MAX_KM:
        return err(f"Maximum home visit distance is {Config.HOME_VISIT_MAX_KM} km")

    service_fee = Config.SERVICES[service]
    travel_fee  = calc_travel_fee(distance_km)
    total       = service_fee + travel_fee

    visit = {
        "visit_id":    generate_visit_id(),
        "user_id":     request.user["sub"],
        "name":        name,
        "phone":       phone,
        "email":       data.get("email", ""),
        "service":     service,
        "address":     address,
        "landmark":    landmark,
        "date":        date,
        "time":        time,
        "distance_km": distance_km,
        "service_fee": service_fee,
        "travel_fee":  travel_fee,
        "total_price": total,
        "type":        "home",
        "status":      "confirmed",
        "stylist":     "Assigned on arrival",
        "created_at":  datetime.utcnow(),
    }

    db = get_db()
    db.home_visits.insert_one(visit)
    return ok(serialize(visit), "Home visit booked successfully", 201)


# ── Get single ────────────────────────────────────────────────────────────────

@home_visits_bp.route("/<visit_id>", methods=["GET"])
@require_auth
def get_visit(visit_id):
    db  = get_db()
    doc = db.home_visits.find_one({"visit_id": visit_id})
    if not doc:
        return err("Home visit not found", 404)
    return ok(serialize(doc))


# ── Update status ─────────────────────────────────────────────────────────────

@home_visits_bp.route("/<visit_id>", methods=["PATCH"])
@require_auth
def update_visit(visit_id):
    data   = request.get_json() or {}
    status = data.get("status")

    valid = ["confirmed", "pending", "cancelled", "completed", "en_route"]
    if status and status not in valid:
        return err(f"Status must be one of: {valid}")

    db  = get_db()
    doc = db.home_visits.find_one({"visit_id": visit_id})
    if not doc:
        return err("Home visit not found", 404)

    updates = {"updated_at": datetime.utcnow()}
    if status:
        updates["status"] = status

    db.home_visits.update_one({"visit_id": visit_id}, {"$set": updates})
    updated = db.home_visits.find_one({"visit_id": visit_id})
    return ok(serialize(updated), "Visit updated")


# ── Delete ────────────────────────────────────────────────────────────────────

@home_visits_bp.route("/<visit_id>", methods=["DELETE"])
@require_auth
def delete_visit(visit_id):
    db  = get_db()
    res = db.home_visits.delete_one({"visit_id": visit_id})
    if res.deleted_count == 0:
        return err("Home visit not found", 404)
    return ok(message="Home visit cancelled")


# ── Travel fee calculator ─────────────────────────────────────────────────────

@home_visits_bp.route("/calculate-fee", methods=["GET"])
def calculate_fee():
    """Quick fee calculation without creating a booking."""
    try:
        distance_km = float(request.args.get("distance_km", 5))
        service     = request.args.get("service", "")
    except (ValueError, TypeError):
        return err("Invalid distance_km value")

    service_fee = Config.SERVICES.get(service, 0)
    travel_fee  = calc_travel_fee(distance_km)

    return ok({
        "distance_km": distance_km,
        "service":     service,
        "service_fee": service_fee,
        "travel_fee":  travel_fee,
        "total":       service_fee + travel_fee,
        "note":        f"Base ₹{Config.BASE_TRAVEL_FEE} up to 5km · +₹{Config.EXTRA_KM_CHARGE}/km beyond"
    })
