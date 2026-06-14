"""
GroomX v6 - Salon Finder Routes
GET   /api/salons/          - list salons (filter: open, home_visit, min_rating)
GET   /api/salons/<id>      - get single salon
PATCH /api/salons/<id>      - update salon info (owner only)
"""

from flask import Blueprint, request
from config.database import get_db
from utils import serialize, serialize_list, ok, err, require_auth, require_owner

salons_bp = Blueprint("salons", __name__)


# ── List salons ───────────────────────────────────────────────────────────────

@salons_bp.route("/", methods=["GET"])
def list_salons():
    db    = get_db()
    query = {}

    is_open    = request.args.get("open")
    home_visit = request.args.get("home_visit")
    min_rating = request.args.get("min_rating")
    search     = request.args.get("search", "").strip()

    if is_open is not None:
        query["is_open"] = is_open.lower() == "true"

    if home_visit is not None:
        query["home_visit"] = home_visit.lower() == "true"

    if min_rating:
        query["rating"] = {"$gte": float(min_rating)}

    if search:
        query["$or"] = [
            {"name":    {"$regex": search, "$options": "i"}},
            {"address": {"$regex": search, "$options": "i"}},
        ]

    docs = list(db.salons.find(query).sort("distance_km", 1))
    return ok({
        "salons": serialize_list(docs),
        "total":  len(docs),
    })


# ── Single salon ──────────────────────────────────────────────────────────────

@salons_bp.route("/<salon_id>", methods=["GET"])
def get_salon(salon_id):
    db  = get_db()
    doc = db.salons.find_one({"salon_id": salon_id})
    if not doc:
        return err("Salon not found", 404)
    return ok(serialize(doc))


# ── Update salon profile (owner only) ────────────────────────────────────────

@salons_bp.route("/<salon_id>", methods=["PATCH"])
@require_owner
def update_salon(salon_id):
    data = request.get_json() or {}
    allowed_fields = {"name", "address", "phone", "hours", "is_open", "home_visit"}
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        return err("No valid fields to update")

    db = get_db()
    db.salons.update_one({"salon_id": salon_id}, {"$set": updates})
    updated = db.salons.find_one({"salon_id": salon_id})
    return ok(serialize(updated), "Salon updated")
