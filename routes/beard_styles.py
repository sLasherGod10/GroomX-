"""
GroomX v6 - Beard Styles Routes
GET /api/beard-styles/              - list all styles (with optional ?category= filter)
GET /api/beard-styles/<style_id>    - get single style
"""

from flask import Blueprint, request
from config.database import get_db
from utils import serialize, serialize_list, ok, err

beard_styles_bp = Blueprint("beard_styles", __name__)

VALID_CATEGORIES = {"classic", "short", "modern", "designer", "full", "ethnic"}


@beard_styles_bp.route("/", methods=["GET"])
def list_styles():
    db    = get_db()
    query = {}

    category   = request.args.get("category", "").lower()
    difficulty = request.args.get("difficulty", "").lower()
    max_price  = request.args.get("max_price")
    min_price  = request.args.get("min_price")

    if category and category in VALID_CATEGORIES:
        query["category"] = category

    if difficulty:
        query["difficulty"] = difficulty

    price_filter = {}
    if max_price:
        price_filter["$lte"] = int(max_price)
    if min_price:
        price_filter["$gte"] = int(min_price)
    if price_filter:
        query["price"] = price_filter

    docs = list(db.beard_styles.find(query).sort("price", 1))
    return ok({
        "styles":     serialize_list(docs),
        "total":      len(docs),
        "categories": list(VALID_CATEGORIES),
    })


@beard_styles_bp.route("/<style_id>", methods=["GET"])
def get_style(style_id):
    db  = get_db()
    doc = db.beard_styles.find_one({"style_id": style_id})
    if not doc:
        return err("Beard style not found", 404)
    return ok(serialize(doc))
