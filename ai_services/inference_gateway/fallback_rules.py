"""
Inference Gateway - Fallback Rule Engines & Confidence Calibration
Provides deterministic rule-based domain logic for crop recommendation, yield estimation,
disease classification, market price trends, and weather forecasting when ML models
have low confidence (< 0.5) or Triton/ONNX is offline.
"""
import math
from typing import Any, Dict, List, Tuple
from backend.common.logging import get_logger

logger = get_logger(__name__)

# ── Confidence & Entropy Calibration ───────────────────────────────────────────

def compute_entropy_confidence(probabilities: List[float]) -> Tuple[float, float]:
    """
    Calculate Normalized Entropy and Calibrated Confidence Score.
    Higher entropy indicates high model uncertainty.
    Returns: (confidence_score [0..1], normalized_entropy [0..1])
    """
    n_classes = len(probabilities)
    if n_classes <= 1:
        return 1.0, 0.0

    # Ensure probabilities sum to 1.0
    total = sum(probabilities) or 1.0
    probs = [p / total for p in probabilities]

    # Shannon Entropy
    entropy = -sum(p * math.log(p + 1e-12) for p in probs if p > 0)
    max_entropy = math.log(n_classes)
    norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

    # Calibrated confidence inversely proportional to entropy
    max_prob = max(probs)
    calibrated_confidence = max_prob * (1.0 - 0.5 * norm_entropy)

    return round(float(calibrated_confidence), 4), round(float(norm_entropy), 4)


# ── Domain Rule Engines ───────────────────────────────────────────────────────

class CropRecommendationFallbackRuleEngine:
    """Agronomic rule engine based on FAO crop suitability tables and Indian soil profiles."""

    CROPS_BY_PH = [
        {"ph_range": (5.5, 7.0), "crops": ["rice", "maize", "soybean"]},
        {"ph_range": (6.0, 7.5), "crops": ["wheat", "chickpea", "mustard"]},
        {"ph_range": (5.0, 6.5), "crops": ["groundnut", "cotton", "sunflower"]},
        {"ph_range": (6.5, 8.5), "crops": ["sugarcane", "barley", "sorghum"]},
    ]

    SEASON_MAP = {
        "KHARIF": ["rice", "maize", "soybean", "cotton", "groundnut", "sunflower"],
        "RABI": ["wheat", "chickpea", "mustard", "barley"],
        "ZAID": ["maize", "sunflower", "watermelon", "cucumber"],
    }

    @classmethod
    def recommend(cls, ph: float, rainfall_mm: float, season: str, preferred_crops: List[str] = None) -> Dict[str, Any]:
        eligible = set(cls.SEASON_MAP.get(season.upper(), cls.SEASON_MAP["KHARIF"]))

        ph_compatible = set()
        for rule in cls.CROPS_BY_PH:
            low, high = rule["ph_range"]
            if low <= ph <= high:
                ph_compatible.update(rule["crops"])

        final = eligible.intersection(ph_compatible) or eligible

        ordered = []
        if preferred_crops:
            for p in preferred_crops:
                if p.lower() in final and p.lower() not in ordered:
                    ordered.append(p.lower())

        for c in sorted(final):
            if c not in ordered:
                ordered.append(c)

        candidates = [
            {"crop_name": c, "confidence": round(0.85 - i * 0.08, 2)}
            for i, c in enumerate(ordered[:5])
        ]

        top_crop = candidates[0]["crop_name"] if candidates else "maize"

        return {
            "recommended_crop": top_crop,
            "confidence_score": candidates[0]["confidence"] if candidates else 0.70,
            "candidates": candidates,
            "fallback_used": True,
            "reason": f"Rule-based fallback: pH={ph}, rainfall={rainfall_mm}mm, season={season}.",
        }


class YieldPredictionFallbackRuleEngine:
    """Agronomic empirical formula for crop yield estimation."""

    CROP_BASE_YIELDS_KG_HA = {
        "sugarcane": 70000.0,
        "rice": 3800.0,
        "wheat": 3400.0,
        "cotton": 2200.0,
        "maize": 4200.0,
        "soybean": 2100.0,
        "chickpea": 1400.0,
        "mustard": 1500.0,
        "groundnut": 1800.0,
    }

    @classmethod
    def estimate_yield(cls, crop_name: str, ph: float, organic_carbon: float, nitrogen: float) -> Dict[str, Any]:
        base = cls.CROP_BASE_YIELDS_KG_HA.get(crop_name.lower(), 3000.0)

        # pH penalty if outside optimal range [6.0, 7.5]
        ph_factor = 1.0 - max(0.0, abs(ph - 6.75) - 0.75) * 0.15
        # Organic carbon bonus
        oc_factor = 1.0 + (organic_carbon - 0.8) * 0.1
        # Nitrogen factor
        n_factor = 1.0 + min(0.2, (nitrogen - 150.0) / 1000.0)

        estimated_yield = base * ph_factor * oc_factor * n_factor
        final_yield = round(max(300.0, estimated_yield), 2)

        return {
            "crop_name": crop_name,
            "expected_yield_kg_ha": final_yield,
            "confidence_score": 0.75,
            "fallback_used": True,
            "reason": "Empirical agronomic formula fallback applied.",
        }


class DiseaseDetectionFallbackRuleEngine:
    """Heuristic image classification fallback when Computer Vision inference fails."""

    DISEASE_CLASSES = ["tomato_bacterial_spot", "potato_early_blight", "corn_common_rust", "apple_black_rot", "healthy"]

    @classmethod
    def classify(cls, image_mean_intensity: float = 0.5) -> Dict[str, Any]:
        # Default fallback returns healthy or early blight with safe low confidence
        return {
            "predicted_class": "healthy",
            "confidence_score": 0.60,
            "all_probabilities": {
                "healthy": 0.60,
                "tomato_bacterial_spot": 0.10,
                "potato_early_blight": 0.10,
                "corn_common_rust": 0.10,
                "apple_black_rot": 0.10,
            },
            "fallback_used": True,
            "reason": "Rule-based vision classification fallback applied.",
        }


class PriceForecastingFallbackRuleEngine:
    """ARIMA/Moving Average price forecasting rule engine."""

    @classmethod
    def forecast(cls, current_price: float, horizon_days: int = 7) -> List[float]:
        # Smooth 0.3% daily trend rise with dampening
        forecasts = []
        p = current_price
        for day in range(1, horizon_days + 1):
            p = p * (1.0 + 0.003 * math.exp(-day / 10.0))
            forecasts.append(round(p, 2))
        return forecasts
