"""
routes/soil.py - Soil Analysis API
POST /api/soil/analyse
"""
import json
import pickle
from pathlib import Path

import numpy as np
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from database.init_db import get_connection

soil_bp = Blueprint("soil", __name__)

BASE = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE / "models"

_model = None
_scaler = None
_soil_type_enc = None
_label_enc = None
_feature_meta = None

MICRO_THRESHOLDS = {
    "Zn": {"low": "Apply 25 kg/ha Zinc Sulphate as soil application, repeat every 2-3 seasons."},
    "Fe": {"low": "Foliar spray of 0.5% Ferrous Sulphate solution during early growth stages."},
    "Mn": {"low": "Apply Manganese Sulphate 0.5% foliar spray at vegetative stage."},
    "Cu": {"low": "Apply Copper Sulphate 2-3 kg/ha via soil, avoid over-application (toxic in excess)."},
    "B": {"low": "Apply Borax 10 kg/ha before sowing, especially important for oilseeds/pulses."},
}


def _load_artifacts():
    global _model, _scaler, _soil_type_enc, _label_enc, _feature_meta
    if _model is not None:
        return
    with open(MODELS_DIR / "soil_model.pkl", "rb") as f:
        _model = pickle.load(f)
    with open(MODELS_DIR / "soil_scaler.pkl", "rb") as f:
        _scaler = pickle.load(f)
    with open(MODELS_DIR / "soil_type_encoder.pkl", "rb") as f:
        _soil_type_enc = pickle.load(f)
    with open(MODELS_DIR / "soil_label_encoder.pkl", "rb") as f:
        _label_enc = pickle.load(f)
    with open(MODELS_DIR / "soil_feature_order.json", encoding="utf-8") as f:
        _feature_meta = json.load(f)


def _safe_transform(encoder, value, fallback_index=0):
    try:
        return int(encoder.transform([value])[0])
    except ValueError:
        return fallback_index


def _score_component(value, low, high, ideal_low, ideal_high):
    if ideal_low <= value <= ideal_high:
        return 100
    if value < ideal_low:
        span = max(ideal_low - low, 1e-6)
        return max(0, 100 * (1 - (ideal_low - value) / span))
    span = max(high - ideal_high, 1e-6)
    return max(0, 100 * (1 - (value - ideal_high) / span))


def _compute_health_score(N, P, K, ph, oc, ec):
    n_score = _score_component(N, 0, 150, 60, 120)
    p_score = _score_component(P, 0, 150, 25, 60)
    k_score = _score_component(K, 0, 210, 40, 120)
    ph_score = _score_component(ph, 3.5, 9.0, 6.0, 7.5)
    oc_score = _score_component(oc, 0.1, 3.0, 0.75, 2.0)
    ec_score = 100 if ec <= 1.0 else max(0, 100 - (ec - 1.0) * 40)
    return round(
        n_score * 0.22 + p_score * 0.18 + k_score * 0.18 +
        ph_score * 0.17 + oc_score * 0.15 + ec_score * 0.10, 1
    ), {"N": n_score, "P": p_score, "K": k_score, "pH": ph_score,
        "Organic Carbon": oc_score, "EC": ec_score}


def _fertilizer_advice(N, P, K, ph, soil_type, crop):
    steps = []
    if N < 60:
        steps.append("Nitrogen is low - apply Urea (46% N) in 2-3 split doses; consider Green Manuring before next season.")
    elif N > 140:
        steps.append("Nitrogen is high - reduce urea dose to avoid lodging and nitrate leaching; prioritise P and K instead.")
    if P < 25:
        steps.append("Phosphorus is low - apply DAP or SSP at sowing time, placed near the root zone for better uptake.")
    if K < 40:
        steps.append("Potassium is low - apply Muriate of Potash (MOP); important for fruit/grain filling and disease resistance.")
    if ph < 6.0:
        lime_dose = round((6.5 - ph) * 500, 0)
        steps.append(f"Soil is acidic (pH {ph}) - apply agricultural lime, roughly {lime_dose} kg/ha, incorporated before sowing.")
    elif ph > 7.8:
        steps.append(f"Soil is alkaline (pH {ph}) - apply Gypsum or elemental Sulphur and add well-decomposed organic matter/compost.")
    if soil_type in ("Desert", "Red", "Laterite"):
        steps.append(f"{soil_type} soils hold water and nutrients poorly - add 5-10 tonnes/ha of farmyard manure or compost to improve structure.")
    if not steps:
        steps.append(f"Nutrient levels look well balanced for {crop or 'most crops'} - maintain with regular compost/FYM application.")
    return steps[:5]


@soil_bp.route("/api/soil/analyse", methods=["POST"])
@login_required
def analyse():
    _load_artifacts()
    data = request.get_json(force=True, silent=True) or {}

    required = ["soil_type", "N", "P", "K", "ph", "organic_carbon", "ec"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        N, P, K = float(data["N"]), float(data["P"]), float(data["K"])
        ph = float(data["ph"])
        oc = float(data["organic_carbon"])
        ec = float(data["ec"])
    except (TypeError, ValueError):
        return jsonify({"error": "N, P, K, ph, organic_carbon, ec must be numeric."}), 400

    soil_type = data["soil_type"]
    crop = data.get("crop", "")
    deficiencies = data.get("deficiencies", [])  # e.g. ["Zn", "Fe"]

    numeric_features = _feature_meta["numeric_features"]
    numeric_vals = [N, P, K, ph, oc, ec]
    numeric_scaled = _scaler.transform([numeric_vals])[0]
    soil_val = _safe_transform(_soil_type_enc, soil_type)

    X = np.array([list(numeric_scaled) + [soil_val]])
    proba = _model.predict_proba(X)[0]
    pred_idx = int(np.argmax(proba))
    health_class = _label_enc.classes_[pred_idx]

    health_score, component_scores = _compute_health_score(N, P, K, ph, oc, ec)

    if health_score >= 75:
        color = "green"
    elif health_score >= 50:
        color = "yellow"
    else:
        color = "red"

    deficiency_report = []
    for micro in deficiencies:
        if micro in MICRO_THRESHOLDS:
            deficiency_report.append({
                "nutrient": micro,
                "severity": "Deficient",
                "advice": MICRO_THRESHOLDS[micro]["low"],
            })

    steps = _fertilizer_advice(N, P, K, ph, soil_type, crop)

    if health_score >= 75:
        timeline = "Already in good condition - maintain with routine practice (ongoing)."
    elif health_score >= 50:
        timeline = "Expect noticeable improvement within 1-2 cropping seasons (4-8 months) with the steps above."
    else:
        timeline = "Significant recovery likely needs 2-3 cropping seasons (8-15 months) of sustained soil-building."

    result = {
        "health_score": health_score,
        "health_class": health_class,
        "color": color,
        "component_scores": {k: round(v, 1) for k, v in component_scores.items()},
        "deficiencies": deficiency_report,
        "improvement_steps": steps,
        "timeline": timeline,
    }

    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO soil_queries (user_id, crop, soil_type, n, p, k, ph, "
            "organic_carbon, ec, health_score, suggestions_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (current_user.id, crop, soil_type, N, P, K, ph, oc, ec, health_score, json.dumps(result)),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        current_app.logger.warning(f"Could not log soil query: {e}")

    return jsonify(result)
