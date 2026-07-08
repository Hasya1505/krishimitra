"""
routes/crop.py - Crop Recommendation API
POST /api/crop/recommend
"""
import json
import pickle
from pathlib import Path

import numpy as np
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from database.init_db import get_connection

crop_bp = Blueprint("crop", __name__)

BASE = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE / "models"
ASSETS_DIR = BASE / "static" / "assets"

_model = None
_scaler = None
_season_enc = None
_soil_enc = None
_label_enc = None
_feature_meta = None
_crop_info = None


def _load_artifacts():
    global _model, _scaler, _season_enc, _soil_enc, _label_enc, _feature_meta, _crop_info
    if _model is not None:
        return
    with open(MODELS_DIR / "crop_model.pkl", "rb") as f:
        _model = pickle.load(f)
    with open(MODELS_DIR / "crop_scaler.pkl", "rb") as f:
        _scaler = pickle.load(f)
    with open(MODELS_DIR / "season_encoder.pkl", "rb") as f:
        _season_enc = pickle.load(f)
    with open(MODELS_DIR / "soil_encoder.pkl", "rb") as f:
        _soil_enc = pickle.load(f)
    with open(MODELS_DIR / "crop_label_encoder.pkl", "rb") as f:
        _label_enc = pickle.load(f)
    with open(MODELS_DIR / "crop_feature_order.json", encoding="utf-8") as f:
        _feature_meta = json.load(f)
    with open(ASSETS_DIR / "crop_info.json", encoding="utf-8") as f:
        _crop_info = json.load(f)


def _safe_transform(encoder, value, fallback_index=0):
    """LabelEncoder.transform errors on unseen labels; fall back gracefully."""
    try:
        return int(encoder.transform([value])[0])
    except ValueError:
        return fallback_index


@crop_bp.route("/api/crop/recommend", methods=["POST"])
@login_required
def recommend():
    _load_artifacts()
    data = request.get_json(force=True, silent=True) or {}

    required = ["N", "P", "K", "ph", "temperature", "humidity", "rainfall", "season", "soil_type"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        numeric = [
            float(data["N"]), float(data["P"]), float(data["K"]),
            float(data["temperature"]), float(data["humidity"]),
            float(data["ph"]), float(data["rainfall"]),
        ]
    except (TypeError, ValueError):
        return jsonify({"error": "N, P, K, temperature, humidity, ph, rainfall must be numeric."}), 400

    numeric_features = _feature_meta["numeric_features"]
    numeric_scaled = _scaler.transform([numeric])[0]

    season_val = _safe_transform(_season_enc, data["season"])
    soil_val = _safe_transform(_soil_enc, data["soil_type"])

    X = np.array([list(numeric_scaled) + [season_val, soil_val]])

    proba = _model.predict_proba(X)[0]
    top_idx = np.argsort(proba)[::-1][:5]

    results = []
    for idx in top_idx:
        crop_name = _label_enc.classes_[idx]
        info = _crop_info.get(crop_name, {})
        results.append({
            "crop": crop_name,
            "confidence": round(float(proba[idx]) * 100, 1),
            "emoji": info.get("emoji", "🌿"),
            "hindi_name": info.get("hindi", ""),
            "best_season": info.get("season", data["season"]),
            "tips": info.get("tips", "Follow standard local agronomic practice for this crop."),
        })

    # Log query
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO crop_queries (user_id, state, district, season, n, p, k, ph, "
            "temperature, humidity, rainfall, top_crop, results_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                current_user.id, data.get("state", ""), data.get("district", ""),
                data["season"], numeric[0], numeric[1], numeric[2], numeric[5],
                numeric[3], numeric[4], numeric[6],
                results[0]["crop"], json.dumps(results),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        current_app.logger.warning(f"Could not log crop query: {e}")

    return jsonify({"results": results})
