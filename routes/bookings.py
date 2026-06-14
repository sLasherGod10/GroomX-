"""
GroomX v6 - Bookings Routes
GET    /api/bookings/            - list all bookings (owner) or own bookings
POST   /api/bookings/            - create a booking
GET    /api/bookings/<id>        - get single booking
PATCH  /api/bookings/<id>        - update status
DELETE /api/bookings/<id>        - cancel / delete
GET    /api/bookings/slots       - available time slots for a date+stylist
"""

from flask import Blueprint, request
from config.database import get_db
from utils import generate_booking_id, serialize, serialize_list, ok, err, require_auth
from config.settings import Config
from datetime import datetime

bookings_bp = Blueprint("bookings", __name__)

ALL_SLOTS = [
    "9:00 AM","9:30 AM","10:00 AM","10:30 AM","11:00 AM","11:30 AM",
    "12:00 PM","12:30 PM","1:00 PM","1:30 PM","2:00 PM","2:30 PM",
    "3:00 PM","3:30 PM","4:00 PM","4:30 PM","5:00 PM",
]

STYLISTS = ["Arjun", "Meera", "Kabir", "Priya"]


# ── List / filter bookings ────────────────────────────────────────────────────

@bookings_bp.route("/", methods=["GET"])
@require_auth
def list_bookings():
    db     = get_db()
    query  = {}
    status = request.args.get("status")
    date   = request.args.get("date")
    stylist = request.args.get("stylist")

    if status:
        query["status"] = status
    if date:
        query["date"] = date
    if stylist:
        query["stylist"] = stylist

    # Customers can only see their own bookings
    if request.user.get("role") == "customer":
        query["user_id"] = request.user["sub"]

    docs = list(db.bookings.find(query).sort("created_at", -1))
    return ok(serialize_list(docs))


# ── Create booking ────────────────────────────────────────────────────────────

@bookings_bp.route("/", methods=["POST"])
@require_auth
def create_booking():
    data    = request.get_json() or {}
    name    = data.get("name", "").strip()
    phone   = data.get("phone", "").strip()
    service = data.get("service", "").strip()
    stylist = data.get("stylist", "").strip()
    date    = data.get("date", "").strip()
    time    = data.get("time", "").strip()

    # Validation
    if not all([name, phone, service, stylist, date, time]):
        return err("All fields (name, phone, service, stylist, date, time) are required")

    if stylist not in STYLISTS:
        return err(f"Stylist must be one of: {', '.join(STYLISTS)}")

    if time not in ALL_SLOTS:
        return err(f"Invalid time slot")

    if service not in Config.SERVICES:
        return err(f"Unknown service. Valid: {list(Config.SERVICES.keys())}")

    db = get_db()

    # Check slot not already taken
    clash = db.bookings.find_one({
        "date": date, "stylist": stylist, "time": time,
        "status": {"$in": ["confirmed", "pending"]}
    })
    if clash:
        return err(f"Slot {time} is already booked for {stylist} on {date}", 409)

    booking = {
        "booking_id": generate_booking_id(),
        "user_id":    request.user["sub"],
        "name":       name,
        "phone":      phone,
        "email":      data.get("email", ""),
        "service":    service,
        "price":      Config.SERVICES[service],
        "stylist":    stylist,
        "date":       date,
        "time":       time,
        "type":       "salon",
        "status":     "pending",
        "created_at": datetime.utcnow(),
    }
    db.bookings.insert_one(booking)
    return ok(serialize(booking), "Booking confirmed", 201)


# ── Get single booking ────────────────────────────────────────────────────────

@bookings_bp.route("/<booking_id>", methods=["GET"])
@require_auth
def get_booking(booking_id):
    db  = get_db()
    doc = db.bookings.find_one({"booking_id": booking_id})
    if not doc:
        return err("Booking not found", 404)
    return ok(serialize(doc))


# ── Update booking status ─────────────────────────────────────────────────────

@bookings_bp.route("/<booking_id>", methods=["PATCH"])
@require_auth
def update_booking(booking_id):
    data   = request.get_json() or {}
    status = data.get("status")

    valid_statuses = ["confirmed", "pending", "cancelled", "completed"]
    if status and status not in valid_statuses:
        return err(f"Status must be one of: {valid_statuses}")

    db  = get_db()
    doc = db.bookings.find_one({"booking_id": booking_id})
    if not doc:
        return err("Booking not found", 404)

    updates = {"updated_at": datetime.utcnow()}
    if status:
        updates["status"] = status

    db.bookings.update_one({"booking_id": booking_id}, {"$set": updates})
    updated = db.bookings.find_one({"booking_id": booking_id})
    return ok(serialize(updated), "Booking updated")


# ── Delete booking ────────────────────────────────────────────────────────────

@bookings_bp.route("/<booking_id>", methods=["DELETE"])
@require_auth
def delete_booking(booking_id):
    db  = get_db()
    res = db.bookings.delete_one({"booking_id": booking_id})
    if res.deleted_count == 0:
        return err("Booking not found", 404)
    return ok(message="Booking deleted")


# ── Get available slots ───────────────────────────────────────────────────────

@bookings_bp.route("/slots", methods=["GET"])
def get_slots():
    """Return available and taken slots for a given date and stylist."""
    date    = request.args.get("date")
    stylist = request.args.get("stylist")

    if not date or not stylist:
        return err("date and stylist query params are required")

    db = get_db()
    taken_docs = db.bookings.find({
        "date": date, "stylist": stylist,
        "status": {"$in": ["confirmed", "pending"]}
    }, {"time": 1})

    taken = {doc["time"] for doc in taken_docs}

    slots = [
        {"time": s, "available": s not in taken}
        for s in ALL_SLOTS
    ]
    return ok({"slots": slots, "date": date, "stylist": stylist})
