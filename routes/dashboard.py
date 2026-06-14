"""
GroomX v6 - Dashboard / Analytics Routes
GET /api/dashboard/stats      - key metrics (total, revenue, pending…)
GET /api/dashboard/charts     - chart-ready data (by-day, by-service)
GET /api/dashboard/pending    - pending bookings queue for owner panel
"""

from flask import Blueprint, request
from config.database import get_db
from utils import serialize_list, ok, require_auth, require_owner
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard", __name__)


# ── Key stats ─────────────────────────────────────────────────────────────────

@dashboard_bp.route("/stats", methods=["GET"])
@require_auth
def stats():
    db    = get_db()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    role  = request.user.get("role", "customer")
    uid   = request.user.get("sub")

    # Customers see only their own; owners see all
    bk_q = {} if role == "owner" else {"user_id": uid}
    hv_q = {} if role == "owner" else {"user_id": uid}

    total_bookings = db.bookings.count_documents(bk_q)
    total_visits   = db.home_visits.count_documents(hv_q)

    today_bks  = list(db.bookings.find({**bk_q, "date": today, "status": "confirmed"}))
    today_rev  = sum(b.get("price", 0) for b in today_bks)
    today_hvs  = list(db.home_visits.find({**hv_q, "date": today, "status": "confirmed"}))
    today_rev += sum(v.get("total_price", 0) for v in today_hvs)

    pending_bks = db.bookings.count_documents({**bk_q, "status": "pending"})
    pending_hvs = db.home_visits.count_documents({**hv_q, "status": "pending"})

    total_scans = db.ai_scans.count_documents({})

    all_phones_bk = db.bookings.distinct("phone", bk_q)
    all_phones_hv = db.home_visits.distinct("phone", hv_q)
    unique_clients = len(set(all_phones_bk + all_phones_hv))

    return ok({
        "total_bookings":      total_bookings,
        "total_home_visits":   total_visits,
        "today_revenue":       today_rev,
        "pending_bookings":    pending_bks,
        "pending_home_visits": pending_hvs,
        "total_pending":       pending_bks + pending_hvs,
        "ai_scans":            total_scans,
        "unique_clients":      unique_clients,
        "today_date":          today,
    })


# ── Chart data ────────────────────────────────────────────────────────────────

@dashboard_bp.route("/charts", methods=["GET"])
@require_auth
def charts():
    db   = get_db()
    role = request.user.get("role", "customer")
    uid  = request.user.get("sub")
    bk_q = {} if role == "owner" else {"user_id": uid}
    hv_q = {} if role == "owner" else {"user_id": uid}

    # Last 7 days
    by_day = {}
    for i in range(6, -1, -1):
        day = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        cnt  = db.bookings.count_documents({**bk_q, "date": day})
        cnt += db.home_visits.count_documents({**hv_q, "date": day})
        by_day[day] = cnt

    # By service
    bk_svc = list(db.bookings.aggregate([
        {"$match": bk_q},
        {"$group": {"_id": "$service", "count": {"$sum": 1}, "revenue": {"$sum": "$price"}}},
        {"$sort":  {"count": -1}},
    ]))
    hv_svc = list(db.home_visits.aggregate([
        {"$match": hv_q},
        {"$group": {"_id": "$service", "count": {"$sum": 1}, "revenue": {"$sum": "$service_fee"}}},
        {"$sort":  {"count": -1}},
    ]))
    by_service = {}
    for row in bk_svc + hv_svc:
        k = row["_id"]
        if k not in by_service:
            by_service[k] = {"count": 0, "revenue": 0}
        by_service[k]["count"]   += row["count"]
        by_service[k]["revenue"] += row.get("revenue", 0)

    # By stylist
    by_stylist = {
        row["_id"]: row["count"]
        for row in db.bookings.aggregate([
            {"$match": bk_q},
            {"$group": {"_id": "$stylist", "count": {"$sum": 1}}},
            {"$sort":  {"count": -1}},
        ])
    }

    # By status
    by_status = {}
    for row in list(db.bookings.aggregate([
        {"$match": bk_q},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ])) + list(db.home_visits.aggregate([
        {"$match": hv_q},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ])):
        by_status[row["_id"]] = by_status.get(row["_id"], 0) + row["count"]

    return ok({
        "by_day":     by_day,
        "by_service": by_service,
        "by_stylist": by_stylist,
        "by_status":  by_status,
    })


# ── Pending queue ─────────────────────────────────────────────────────────────

@dashboard_bp.route("/pending", methods=["GET"])
@require_auth
def pending_queue():
    db   = get_db()
    role = request.user.get("role", "customer")
    uid  = request.user.get("sub")
    bk_q = {"status": "pending"} if role == "owner" else {"status": "pending", "user_id": uid}
    hv_q = {"status": "pending"} if role == "owner" else {"status": "pending", "user_id": uid}

    pending_bks = list(db.bookings.find(bk_q).sort("created_at", 1))
    pending_hvs = list(db.home_visits.find(hv_q).sort("created_at", 1))

    for hv in pending_hvs:
        hv["is_home_visit"] = True
        hv["booking_id"]    = hv.get("visit_id", "")
        hv["price"]         = hv.get("total_price", 0)

    all_pending = serialize_list(pending_bks) + serialize_list(pending_hvs)
    all_pending.sort(key=lambda x: x.get("date", ""))

    return ok({
        "pending":       all_pending,
        "total_pending": len(all_pending),
    })


# ── Accept / decline (owner only) ────────────────────────────────────────────

@dashboard_bp.route("/pending/<record_id>/accept", methods=["POST"])
@require_owner
def accept_pending(record_id):
    db  = get_db()
    res = db.bookings.update_one(
        {"booking_id": record_id}, {"$set": {"status": "confirmed"}}
    )
    if res.matched_count == 0:
        res = db.home_visits.update_one(
            {"visit_id": record_id}, {"$set": {"status": "confirmed"}}
        )
    if res.matched_count == 0:
        return ok(message="Not found (may have already been actioned)")
    return ok(message="Appointment confirmed")


@dashboard_bp.route("/pending/<record_id>/decline", methods=["POST"])
@require_owner
def decline_pending(record_id):
    db  = get_db()
    res = db.bookings.update_one(
        {"booking_id": record_id}, {"$set": {"status": "cancelled"}}
    )
    if res.matched_count == 0:
        res = db.home_visits.update_one(
            {"visit_id": record_id}, {"$set": {"status": "cancelled"}}
        )
    if res.matched_count == 0:
        return ok(message="Not found")
    return ok(message="Appointment declined")
