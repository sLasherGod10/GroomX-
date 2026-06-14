"""
GroomX v6 - MongoDB Database Initialization
Uses Flask-PyMongo for connection management.
"""

from flask_pymongo import PyMongo
from datetime import datetime

mongo = PyMongo()


def init_db(app):
    """Initialize MongoDB connection and seed default data."""
    mongo.init_app(app)

    with app.app_context():
        _create_indexes()
        _seed_data()

    print("  ✦ MongoDB connected successfully")


def get_db():
    """Return the MongoDB database instance."""
    return mongo.db


# ── Indexes ─────────────────────────────────────────────────────────────────

def _create_indexes():
    db = mongo.db

    # Users – unique email
    db.users.create_index("email", unique=True)

    # Bookings – quick lookup by date, status, stylist
    db.bookings.create_index("date")
    db.bookings.create_index("status")
    db.bookings.create_index("stylist")
    db.bookings.create_index("booking_id", unique=True)

    # Home visits
    db.home_visits.create_index("date")
    db.home_visits.create_index("status")
    db.home_visits.create_index("visit_id", unique=True)

    # AI scans
    db.ai_scans.create_index("created_at")


# ── Seed data ────────────────────────────────────────────────────────────────

def _seed_data():
    db = mongo.db

    # ── Salons ────────────────────────────────────────────
    if db.salons.count_documents({}) == 0:
        salons = [
            {"salon_id": "S001", "name": "GroomX Flagship", "address": "MG Road, Nagpur",
             "distance_km": 0.2, "rating": 4.9, "is_open": True, "type": "flagship",
             "home_visit": True, "phone": "+91 98765 43210", "hours": "9AM–6PM",
             "lat": 21.1458, "lng": 79.0882},
            {"salon_id": "S002", "name": "GroomX South", "address": "Dharampeth, Nagpur",
             "distance_km": 1.8, "rating": 4.7, "is_open": True, "type": "flagship",
             "home_visit": True, "phone": "+91 98765 43211", "hours": "9AM–7PM",
             "lat": 21.1320, "lng": 79.0750},
            {"salon_id": "S003", "name": "Style Hub", "address": "Sitabuldi, Nagpur",
             "distance_km": 2.4, "rating": 4.5, "is_open": True, "type": "partner",
             "home_visit": False, "phone": "+91 98765 43212", "hours": "10AM–8PM",
             "lat": 21.1500, "lng": 79.0800},
            {"salon_id": "S004", "name": "The Barber Co.", "address": "Ramdaspeth, Nagpur",
             "distance_km": 3.1, "rating": 4.6, "is_open": False, "type": "partner",
             "home_visit": True, "phone": "+91 98765 43213", "hours": "11AM–9PM",
             "lat": 21.1390, "lng": 79.0920},
            {"salon_id": "S005", "name": "Fades & Blades", "address": "Sadar, Nagpur",
             "distance_km": 3.8, "rating": 4.3, "is_open": True, "type": "partner",
             "home_visit": False, "phone": "+91 98765 43214", "hours": "9AM–6PM",
             "lat": 21.1540, "lng": 79.0950},
            {"salon_id": "S006", "name": "GroomX Express", "address": "Koradi Road, Nagpur",
             "distance_km": 4.2, "rating": 4.8, "is_open": True, "type": "flagship",
             "home_visit": True, "phone": "+91 98765 43215", "hours": "8AM–8PM",
             "lat": 21.1600, "lng": 79.0700},
            {"salon_id": "S007", "name": "Razor & Comb", "address": "Itwari, Nagpur",
             "distance_km": 5.5, "rating": 4.4, "is_open": True, "type": "partner",
             "home_visit": False, "phone": "+91 98765 43216", "hours": "10AM–7PM",
             "lat": 21.1480, "lng": 79.1020},
            {"salon_id": "S008", "name": "The Groom Room", "address": "Manewada, Nagpur",
             "distance_km": 6.2, "rating": 4.2, "is_open": False, "type": "partner",
             "home_visit": True, "phone": "+91 98765 43217", "hours": "10AM–8PM",
             "lat": 21.1250, "lng": 79.0850},
        ]
        db.salons.insert_many(salons)

    # ── Beard Styles ─────────────────────────────────────
    if db.beard_styles.count_documents({}) == 0:
        styles = [
            {"style_id": "BS01", "name": "Classic Full Beard",   "category": "classic",  "tag": "The Timeless Choice",      "description": "Grown naturally with precision neckline and cheek line. The enduring symbol of masculine refinement.", "price": 350, "duration_min": 45, "difficulty": "easy",     "emoji": "🧔"},
            {"style_id": "BS02", "name": "Corporate Stubble",    "category": "short",    "tag": "Sharp & Professional",     "description": "5-7mm precision stubble, perfectly uniform. The modern professional look with a rugged edge.",           "price": 200, "duration_min": 25, "difficulty": "easy",     "emoji": "🪒"},
            {"style_id": "BS03", "name": "Faded Beard",          "category": "modern",   "tag": "Contemporary Classic",     "description": "Skin fade blending seamlessly into a medium beard. Incredible contrast and modern elegance.",           "price": 400, "duration_min": 50, "difficulty": "medium",   "emoji": "🧔‍♂️"},
            {"style_id": "BS04", "name": "Bandholz",             "category": "designer", "tag": "Bold Statement",           "description": "Long, shaped beard paired with a full moustache. Viking-inspired power for bold personalities.",         "price": 500, "duration_min": 65, "difficulty": "advanced", "emoji": "🎭"},
            {"style_id": "BS05", "name": "Van Dyke",             "category": "short",    "tag": "European Aristocrat",      "description": "Goatee plus disconnected moustache. Sharp, distinguished — European aristocratic flair.",                "price": 300, "duration_min": 35, "difficulty": "medium",   "emoji": "🪒"},
            {"style_id": "BS06", "name": "Garibaldi",            "category": "classic",  "tag": "The Naturalist",           "description": "Wide, rounded beard with natural volume. The approachable woodsman aesthetic redefined.",                "price": 350, "duration_min": 40, "difficulty": "easy",     "emoji": "🧔"},
            {"style_id": "BS07", "name": "Sharp Contour",        "category": "modern",   "tag": "Geometric Precision",      "description": "Mathematical precision — geometric lines, crisp edges. Architecture expressed in facial hair.",            "price": 450, "duration_min": 55, "difficulty": "advanced", "emoji": "🧔‍♂️"},
            {"style_id": "BS08", "name": "Circle Beard",         "category": "designer", "tag": "The Modern Classic",       "description": "Rounded chin beard connected to a shaped moustache. The quintessential modern gentleman.",               "price": 280, "duration_min": 30, "difficulty": "easy",     "emoji": "🎭"},
            {"style_id": "BS09", "name": "Norse Viking",         "category": "full",     "tag": "Legendary Status",         "description": "Long, layered beard with optional braiding. Statement-making, commanding, legendary.",                    "price": 600, "duration_min": 80, "difficulty": "advanced", "emoji": "🧔"},
            {"style_id": "BS10", "name": "Anchor Beard",         "category": "full",     "tag": "Maritime Elegance",        "description": "Pointed chin beard meets pencil moustache. Neat, angular — the captain's distinguished choice.",         "price": 320, "duration_min": 38, "difficulty": "medium",   "emoji": "🧔‍♂️"},
            {"style_id": "BS11", "name": "Balbo",                "category": "short",    "tag": "Italian Sophistication",   "description": "Separated moustache and chin beard. Named after Italian Marshal Italo Balbo. Suave and refined.",         "price": 260, "duration_min": 32, "difficulty": "medium",   "emoji": "🪒"},
            {"style_id": "BS12", "name": "Ducktail",             "category": "designer", "tag": "The Gentleman Rebel",      "description": "Fuller on the sides, pointed at the chin. The gentleman outlaw — refined yet daring.",                    "price": 420, "duration_min": 52, "difficulty": "medium",   "emoji": "🎭"},
            {"style_id": "BS13", "name": "Rajput Moustache",     "category": "ethnic",   "tag": "Heritage & Pride",         "description": "Thick, majestic curled moustache inspired by Rajput warrior tradition. Cultural pride in every curl.",   "price": 380, "duration_min": 45, "difficulty": "medium",   "emoji": "🧔"},
            {"style_id": "BS14", "name": "Maratha Warrior",      "category": "ethnic",   "tag": "Royal Heritage",           "description": "Full beard with waxed upturned moustache. Inspired by Maratha warrior culture — regal and fierce.",     "price": 450, "duration_min": 55, "difficulty": "advanced", "emoji": "🧔‍♂️"},
            {"style_id": "BS15", "name": "Designer Stubble Art", "category": "modern",   "tag": "Avant-Garde",              "description": "Artistic shaved patterns within precision stubble. Your beard as a canvas for self-expression.",           "price": 550, "duration_min": 70, "difficulty": "pro",      "emoji": "🪒"},
            {"style_id": "BS16", "name": "The Yeard",            "category": "full",     "tag": "A Year's Journey",         "description": "A full year of growth, shaped into a magnificent statement beard. Not just a beard — a journey.",         "price": 700, "duration_min": 90, "difficulty": "pro",      "emoji": "🧔"},
        ]
        db.beard_styles.insert_many(styles)

    # ── Demo Bookings ─────────────────────────────────────
    if db.bookings.count_documents({}) == 0:
        from bson import ObjectId
        demo_bookings = [
            {"booking_id": "GX0001", "name": "Rahul Mehta",  "phone": "9876543210", "email": "", "service": "Classic Cut",        "stylist": "Arjun", "date": "2026-03-20", "time": "10:00 AM", "price": 350,  "status": "confirmed", "created_at": datetime.utcnow()},
            {"booking_id": "GX0002", "name": "Priya Sharma", "phone": "9988776655", "email": "", "service": "Hair Spa",            "stylist": "Meera", "date": "2026-03-20", "time": "11:30 AM", "price": 799,  "status": "confirmed", "created_at": datetime.utcnow()},
            {"booking_id": "GX0003", "name": "Aditya Kumar", "phone": "9123456789", "email": "", "service": "Beard Sculpt",        "stylist": "Kabir", "date": "2026-03-21", "time": "2:00 PM",  "price": 250,  "status": "pending",   "created_at": datetime.utcnow()},
            {"booking_id": "GX0004", "name": "Sneha Patil",  "phone": "9000112233", "email": "", "service": "Color & Highlights",  "stylist": "Priya", "date": "2026-03-22", "time": "3:00 PM",  "price": 1299, "status": "confirmed", "created_at": datetime.utcnow()},
        ]
        db.bookings.insert_many(demo_bookings)

    # ── Demo Users ────────────────────────────────────────
    if db.users.count_documents({}) == 0:
        import bcrypt
        admin_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
        cust_hash  = bcrypt.hashpw(b"pass123",  bcrypt.gensalt())
        db.users.insert_many([
            {"user_id": "U001", "name": "Studio Admin",  "email": "admin@groomx.com",    "password": admin_hash, "role": "owner",    "salon_name": "GroomX Nagpur", "created_at": datetime.utcnow()},
            {"user_id": "U002", "name": "Demo Customer", "email": "customer@groomx.com", "password": cust_hash,  "role": "customer", "created_at": datetime.utcnow()},
        ])

    print("  ✦ Database seeded with demo data")
