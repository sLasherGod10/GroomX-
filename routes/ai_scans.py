"""
GroomX v6 - AI Face Scan Routes
POST /api/ai-scans/log       - log a completed scan result
GET  /api/ai-scans/          - list scans (owner only)
GET  /api/ai-scans/stats     - face shape distribution stats
"""

from flask import Blueprint, request
from config.database import get_db
from utils import serialize, serialize_list, ok, err, require_auth, require_owner
from datetime import datetime

ai_scans_bp = Blueprint("ai_scans", __name__)

VALID_SHAPES = {"oval", "square", "round", "heart", "oblong"}


# ── Log a scan result ─────────────────────────────────────────────────────────

@ai_scans_bp.route("/log", methods=["POST"])
@require_auth
def log_scan():
    data       = request.get_json() or {}
    shape      = data.get("shape", "").lower()
    confidence = float(data.get("confidence", 0))

    if shape not in VALID_SHAPES:
        return err(f"Shape must be one of: {list(VALID_SHAPES)}")

    scan = {
        "user_id":    request.user["sub"],
        "shape":      shape,
        "confidence": confidence,
        "top_cuts":   data.get("top_cuts", []),
        "created_at": datetime.utcnow(),
    }
    db = get_db()
    db.ai_scans.insert_one(scan)
    return ok({"shape": shape, "confidence": confidence}, "Scan logged", 201)


# ── List scans ────────────────────────────────────────────────────────────────

@ai_scans_bp.route("/", methods=["GET"])
@require_owner
def list_scans():
    db   = get_db()
    docs = list(db.ai_scans.find().sort("created_at", -1).limit(100))
    return ok(serialize_list(docs))


# ── Shape distribution stats ──────────────────────────────────────────────────

@ai_scans_bp.route("/stats", methods=["GET"])
@require_owner
def scan_stats():
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$shape", "count": {"$sum": 1}}},
        {"$sort":  {"count": -1}},
    ]
    result = list(db.ai_scans.aggregate(pipeline))
    dist   = {row["_id"]: row["count"] for row in result}
    total  = sum(dist.values())
    return ok({"total_scans": total, "distribution": dist})
