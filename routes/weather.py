"""
routes/weather.py
Open-Meteo and Nominatim are free/keyless, so the browser can call them
directly (see static/js/weather.js). This blueprint adds two small
value-add server-side endpoints that are awkward to do purely in JS:
  GET /api/weather/alerts?tmax=&tmin=&rain=&humidity=   -> agri risk alerts
  GET /api/weather/sowing-calendar                       -> crops to sow now
"""
import json
from datetime import datetime
from pathlib import Path

from flask import Blueprint, request, jsonify
from flask_login import login_required

weather_bp = Blueprint("weather", __name__)

BASE = Path(__file__).resolve().parent.parent
with open(BASE / "static" / "assets" / "crop_info.json", encoding="utf-8") as f:
    CROP_INFO = json.load(f)


def _current_season():
    month = datetime.now().month  # 1-12
    if 6 <= month <= 10:
        return "Kharif"
    elif month >= 11 or month <= 2:
        return "Rabi"
    return "Zaid"


@weather_bp.route("/api/weather/alerts")
@login_required
def alerts():
    def _f(name, default=None):
        val = request.args.get(name)
        try:
            return float(val) if val is not None else default
        except ValueError:
            return default

    tmax = _f("tmax")
    tmin = _f("tmin")
    rain = _f("rain")
    humidity = _f("humidity")

    result = []
    if tmin is not None and tmin <= 4:
        result.append({"level": "danger", "title": "Frost Risk",
                        "message": "Minimum temperature near/below 4°C. Cover nurseries and young seedlings, irrigate lightly in the evening to reduce frost damage."})
    if rain is not None and rain >= 80:
        result.append({"level": "danger", "title": "Excess Rain Warning",
                        "message": "Heavy rainfall expected. Ensure field drainage channels are clear to prevent waterlogging and root damage."})
    if rain is not None and 0 <= rain < 2 and humidity is not None and humidity < 30:
        result.append({"level": "warning", "title": "Drought Watch",
                        "message": "Low rainfall and low humidity detected. Consider mulching and scheduling irrigation to conserve soil moisture."})
    if tmax is not None and tmax >= 40:
        result.append({"level": "warning", "title": "Heat Stress Risk",
                        "message": "High daytime temperatures may stress flowering crops. Irrigate during cooler morning/evening hours."})
    if not result:
        result.append({"level": "ok", "title": "No Major Alerts",
                        "message": "Current conditions look within normal range for most crops in this season."})

    return jsonify({"alerts": result})


@weather_bp.route("/api/weather/sowing-calendar")
@login_required
def sowing_calendar():
    season = _current_season()
    crops = [
        {"crop": name, "emoji": info.get("emoji", "🌿"), "hindi": info.get("hindi", "")}
        for name, info in CROP_INFO.items() if info.get("season") == season
    ]
    return jsonify({"season": season, "recommended_now": crops})
