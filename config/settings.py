"""
GroomX v6 - Configuration Settings
"""

import os
from datetime import timedelta


class Config:
    # ── Flask ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "groomx-secret-key-change-in-production")
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

    # ── MongoDB ────────────────────────────────────────────
    # Change this URI if your MongoDB runs on a different host/port
    # For MongoDB Atlas: mongodb+srv://<user>:<password>@cluster.mongodb.net/
    MONGO_URI = os.environ.get(
        "MONGO_URI",
        "mongodb://localhost:27017/groomx_db"
    )

    # ── JWT / Session ──────────────────────────────────────
    JWT_SECRET = os.environ.get("JWT_SECRET", "groomx-jwt-secret")
    SESSION_LIFETIME = timedelta(days=7)

    # ── Anthropic (for AI face analysis) ──────────────────
    # Set your key: export ANTHROPIC_API_KEY=sk-ant-...
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

    # ── CORS ───────────────────────────────────────────────
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # ── Pricing ────────────────────────────────────────────
    SERVICES = {
        "Classic Cut":       350,
        "Style & Trim":      550,
        "Hair Spa":          799,
        "Beard Sculpt":      250,
        "Color & Highlights": 1299,
        "Full Groom Package": 899,
    }
    BASE_TRAVEL_FEE = 200       # ₹ for up to 5 km
    EXTRA_KM_CHARGE = 30        # ₹ per km beyond 5 km
    HOME_VISIT_MAX_KM = 20
