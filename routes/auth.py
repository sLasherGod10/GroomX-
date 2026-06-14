"""
GroomX v6 - Authentication Routes
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
POST /api/auth/logout
"""

from flask import Blueprint, request
from config.database import get_db
from utils import (
    hash_password, check_password, create_token,
    generate_user_id, serialize, ok, err, require_auth
)
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


# ── Register ─────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name       = data.get("name", "").strip()
    email      = data.get("email", "").strip().lower()
    password   = data.get("password", "")
    role       = data.get("role", "customer")          # customer | owner
    salon_name = data.get("salon_name", "")

    # Validation
    if not name or not email or len(password) < 6:
        return err("Name, email and password (min 6 chars) are required")
    if role not in ("customer", "owner"):
        return err("Role must be 'customer' or 'owner'")

    db = get_db()

    # Duplicate email check
    if db.users.find_one({"email": email}):
        return err("Email already registered", 409)

    user = {
        "user_id":    generate_user_id(),
        "name":       name,
        "email":      email,
        "password":   hash_password(password),
        "role":       role,
        "salon_name": salon_name if role == "owner" else "",
        "created_at": datetime.utcnow(),
        "is_active":  True,
    }
    db.users.insert_one(user)

    token = create_token(user["user_id"], role)
    return ok({
        "token": token,
        "user":  {"user_id": user["user_id"], "name": name, "email": email, "role": role}
    }, "Account created", 201)


# ── Login ─────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return err("Email and password required")

    db   = get_db()
    user = db.users.find_one({"email": email})

    if not user or not check_password(password, user["password"]):
        return err("Invalid email or password", 401)

    token = create_token(user["user_id"], user["role"])
    return ok({
        "token": token,
        "user":  {
            "user_id":    user["user_id"],
            "name":       user["name"],
            "email":      user["email"],
            "role":       user["role"],
            "salon_name": user.get("salon_name", ""),
        }
    }, "Login successful")


# ── Get current user ─────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    db   = get_db()
    user = db.users.find_one({"user_id": request.user["sub"]})
    if not user:
        return err("User not found", 404)
    return ok(serialize(user))


# ── Logout (client-side token discard) ───────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
def logout():
    # JWT is stateless — client just discards the token
    return ok(message="Logged out successfully")


# ── Demo login helper ─────────────────────────────────────────────────────────

@auth_bp.route("/demo", methods=["POST"])
def demo_login():
    data = request.get_json() or {}
    role = data.get("role", "customer")

    demo_map = {
        "customer": {"email": "customer@groomx.com", "password": "pass123"},
        "owner":    {"email": "admin@groomx.com",    "password": "admin123"},
    }
    if role not in demo_map:
        return err("Role must be 'customer' or 'owner'")

    creds   = demo_map[role]
    db      = get_db()
    user    = db.users.find_one({"email": creds["email"]})

    if not user:
        return err("Demo user not found — please restart the server to reseed", 404)

    token = create_token(user["user_id"], user["role"])
    return ok({
        "token": token,
        "user":  {"user_id": user["user_id"], "name": user["name"],
                  "email": user["email"], "role": user["role"]}
    }, f"Signed in as demo {role}")
