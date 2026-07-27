"""
Advisory Service - Crop Recommendation Engine
Builds the feature vector for ML inference and applies rule-based heuristics
when model confidence is below threshold.
"""
from typing import Any, Dict, List, Optional

from backend.common.logging import get_logger

logger = get_logger(__name__)

# Rule-based crop suitability table (fallback when ML confidence < 0.5)
# ph_min, ph_max, rainfall_mm_min, rainfall_mm_max, crops
CROP_RULES = [
    {"ph_range": (5.5, 7.0), "crops": ["rice", "maize", "soybean"]},
    {"ph_range": (6.0, 7.5), "crops": ["wheat", "chickpea", "mustard"]},
    {"ph_range": (5.0, 6.5), "crops": ["groundnut", "cotton", "sunflower"]},
    {"ph_range": (6.5, 8.5), "crops": ["sugarcane", "barley", "sorghum"]},
]

SEASON_CROPS = {
    "KHARIF":  ["rice", "maize", "soybean", "cotton", "groundnut", "sunflower"],
    "RABI":    ["wheat", "chickpea", "mustard", "barley", "pea"],
    "ZAID":    ["maize", "sunflower", "watermelon", "cucumber", "moongbean"],
}


def build_feature_vector(
    soil_data: Optional[Dict[str, Any]],
    weather_snapshot: Optional[Dict[str, Any]],
    plot_area_ha: float,
    season_name: str,
) -> Dict[str, Any]:
    """Assemble the ML input feature dictionary from available data sources."""
    features: Dict[str, Any] = {
        "plot_area_ha": plot_area_ha,
        "season": season_name,
        # Soil features (default to median Indian agricultural soil values if missing)
        "ph_level": float(soil_data.get("ph_level") or 6.5) if soil_data else 6.5,
        "organic_carbon_pct": float(soil_data.get("organic_carbon_percent") or 0.8) if soil_data else 0.8,
        "nitrogen": float(soil_data.get("nitrogen_content") or 200) if soil_data else 200,
        "phosphorus": float(soil_data.get("phosphorus_content") or 30) if soil_data else 30,
        "potassium": float(soil_data.get("potassium_content") or 200) if soil_data else 200,
        # Weather features
        "avg_temp_c": weather_snapshot.get("avg_temp_c", 25.0) if weather_snapshot else 25.0,
        "rainfall_mm": weather_snapshot.get("monthly_rainfall_mm", 100.0) if weather_snapshot else 100.0,
    }
    return features


def apply_rule_based_recommendations(
    features: Dict[str, Any],
    season_name: str,
    preferred_crops: Optional[List[str]] = None,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Heuristic fallback recommendation engine.
    Used when: (a) ML model is unavailable, or (b) model confidence < 0.5.
    """
    ph = features.get("ph_level", 6.5)
    eligible_crops = set(SEASON_CROPS.get(season_name.upper(), SEASON_CROPS["KHARIF"]))

    # Filter by soil pH compatibility
    ph_compatible = set()
    for rule in CROP_RULES:
        ph_min, ph_max = rule["ph_range"]
        if ph_min <= ph <= ph_max:
            ph_compatible.update(rule["crops"])

    final_crops = eligible_crops.intersection(ph_compatible)

    # If user provided preferred crops, boost those to the top of the recommendation list
    ordered_crops: List[str] = []
    if preferred_crops:
        for c in preferred_crops:
            c_lower = c.lower()
            if c_lower in final_crops and c_lower not in ordered_crops:
                ordered_crops.append(c_lower)

    for c in sorted(final_crops):
        if c not in ordered_crops:
            ordered_crops.append(c)

    recommendations = []
    for i, crop in enumerate(ordered_crops[:top_n]):
        # Assign decreasing confidence scores for ranked output
        recommendations.append({
            "crop_name": crop,
            "confidence_score": round(max(0.5, 0.9 - (i * 0.07)), 3),
            "expected_yield_kg_ha": None,  # Requires ML model for precise yield prediction
            "suitability_reason": f"pH {ph} is suitable for {crop}. Season: {season_name}.",
        })

    logger.info(
        "Rule-based crop recommendations generated",
        extra={"crop_count": len(recommendations), "season": season_name, "ph": ph}
    )
    return recommendations
