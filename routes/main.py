"""
routes/main.py - page routes + GNews server-side proxy (keeps API key secret)
"""
import requests
from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    return render_template("landing.html")


@main_bp.route("/home")
@login_required
def home():
    return render_template("home.html", user=current_user)


@main_bp.route("/crop")
@login_required
def crop_page():
    return render_template("crop.html", user=current_user)


@main_bp.route("/soil")
@login_required
def soil_page():
    return render_template("soil.html", user=current_user)


@main_bp.route("/weather")
@login_required
def weather_page():
    return render_template("weather.html", user=current_user)


@main_bp.route("/api/news")
def news():
    """Server-side proxy for GNews so the API key never reaches the browser.
    Falls back to a small static sample if no key is configured / call fails,
    so the landing page never looks broken during local dev."""
    api_key = current_app.config.get("GNEWS_API_KEY")
    fallback = {
        "articles": [
            {"title": "India's Kharif sowing crosses normal pace this season",
             "source": {"name": "Agri Desk"}, "publishedAt": "2026-06-15T00:00:00Z",
             "url": "#", "image": None},
            {"title": "Government expands PM-KISAN direct benefit coverage",
             "source": {"name": "Agri Desk"}, "publishedAt": "2026-06-10T00:00:00Z",
             "url": "#", "image": None},
            {"title": "Monsoon outlook: above-normal rainfall expected in central India",
             "source": {"name": "Agri Desk"}, "publishedAt": "2026-06-05T00:00:00Z",
             "url": "#", "image": None},
        ]
    }
    if not api_key:
        return jsonify(fallback)
    try:
        resp = requests.get(
            "https://gnews.io/api/v4/search",
            params={"q": "india agriculture", "lang": "en", "max": 6, "token": api_key},
            timeout=6,
        )
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException:
        return jsonify(fallback)
