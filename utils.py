"""
GroomX v6 - Shared Utilities
"""

import uuid
from datetime import datetime
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import bcrypt


# ── ID generation ────────────────────────────────────────────────────────────

def generate_booking_id():
    return "GX" + str(int(datetime.utcnow().timestamp()))[-6:]


def generate_visit_id():
    return "HV" + str(int(datetime.utcnow().timestamp()))[-6:]


def generate_user_id():
    return "U" + uuid.uuid4().hex[:8].upper()


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt())


def check_password(plain: str, hashed) -> bool:
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(plain.encode(), hashed)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])


# ── Auth decorator ────────────────────────────────────────────────────────────

def require_auth(f):
    """Protect a route — requires Authorization: Bearer <token> header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


def require_owner(f):
    """Restrict route to salon owner role."""
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if request.user.get("role") != "owner":
            return jsonify({"error": "Owner access required"}), 403
        return f(*args, **kwargs)
    return decorated


# ── MongoDB document serializer ───────────────────────────────────────────────

def serialize(doc: dict) -> dict:
    """Convert MongoDB document to JSON-safe dict."""
    if doc is None:
        return {}
    doc = dict(doc)
    doc.pop("_id", None)                     # remove ObjectId
    for k, v in doc.items():
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
        elif isinstance(v, bytes):
            doc[k] = "<hashed>"              # never expose password bytes
    return doc


def serialize_list(docs) -> list:
    return [serialize(d) for d in docs]


# ── Travel fee calculation ────────────────────────────────────────────────────

def calc_travel_fee(distance_km: float) -> int:
    """Return travel fee in ₹ based on distance."""
    base = 200
    if distance_km <= 5:
        return base
    return base + int((distance_km - 5) * 30)


# ── JSON response helpers ─────────────────────────────────────────────────────

def ok(data=None, message="Success", status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def err(message="Error", status=400):
    return jsonify({"success": False, "error": message}), status
