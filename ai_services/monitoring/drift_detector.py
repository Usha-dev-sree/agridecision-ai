"""
Model Monitoring - Feature Drift Telemetry
Calculates statistical drift between training baselines and real-time features using
Kolmogorov-Smirnov (KS) tests and Population Stability Index (PSI).
"""
import logging
from typing import Any, Dict, List
import numpy as np

logger = logging.getLogger(__name__)


class DriftTelemetryDetector:
    """Detects and alerts on data/feature distribution shifts over time."""

    @staticmethod
    def calculate_ks_drift(
        baseline_sample: List[float],
        current_sample: List[float],
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Evaluate Kolmogorov-Smirnov 2-sample test for continuous variables.
        p-value < alpha indicates statistically significant feature drift.
        """
        if not baseline_sample or not current_sample:
            return {"drift_detected": False, "p_value": 1.0, "statistic": 0.0, "error": "Empty sample data"}

        b_arr = np.array(baseline_sample)
        c_arr = np.array(current_sample)

        try:
            from scipy.stats import ks_2samp
            stat, p_val = ks_2samp(b_arr, c_arr)
            drift_detected = bool(p_val < alpha)
            return {
                "drift_detected": drift_detected,
                "p_value": float(p_val),
                "statistic": float(stat),
                "method": "Kolmogorov-Smirnov"
            }
        except ImportError:
            # Fallback mathematical approximation: compare difference in means scaled by joint std
            logger.warning("scipy is missing. Using mean-variance approximation for KS test.")
            mean_b, std_b = np.mean(b_arr), np.std(b_arr) or 1e-5
            mean_c, std_c = np.mean(c_arr), np.std(c_arr) or 1e-5
            
            # Simple Z-score like distance between distributions
            distance = abs(mean_b - mean_c) / (0.5 * (std_b + std_c))
            drift_detected = bool(distance > 0.6) # threshold for anomaly
            # Synthesize a p-value
            p_val = max(0.001, min(1.0, 1.0 - (distance / 2.0)))
            return {
                "drift_detected": drift_detected,
                "p_value": float(p_val),
                "statistic": float(distance),
                "method": "Mean-Variance distance approximation"
            }

    @staticmethod
    def calculate_psi(
        baseline_sample: List[float],
        current_sample: List[float],
        num_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate Population Stability Index (PSI) between two samples.
        PSI < 0.1: No change.
        0.1 <= PSI < 0.25: Moderate shift.
        PSI >= 0.25: Significant shift.
        """
        if not baseline_sample or not current_sample:
            return {"psi_score": 0.0, "drift_status": "insufficient_data"}

        b_arr = np.array(baseline_sample)
        c_arr = np.array(current_sample)

        try:
            # Setup quantile-based bin boundaries from baseline
            percentiles = np.linspace(0, 100, num_bins + 1)
            bins = np.percentile(b_arr, percentiles)
            # Make sure bins are unique
            bins = np.unique(bins)
            if len(bins) < 2:
                # Add tiny epsilon if all values are identical
                bins = np.array([bins[0] - 1e-5, bins[0] + 1e-5])
                
            # Count values in each bin
            b_counts, _ = np.histogram(b_arr, bins=bins)
            c_counts, _ = np.histogram(c_arr, bins=bins)
            
            # Calculate percentages
            b_pct = b_counts / len(b_arr)
            c_pct = c_counts / len(c_arr)
            
            # Adjust zero counts to prevent division by zero or log(0)
            b_pct = np.where(b_pct == 0, 0.0001, b_pct)
            c_pct = np.where(c_pct == 0, 0.0001, c_pct)
            
            # PSI calculation
            psi = np.sum((b_pct - c_pct) * np.log(b_pct / c_pct))
            
            if psi >= 0.25:
                status = "significant_drift"
            elif psi >= 0.1:
                status = "moderate_drift"
            else:
                status = "no_drift"
                
            return {
                "psi_score": float(psi),
                "drift_status": status,
                "bin_counts_baseline": b_counts.tolist(),
                "bin_counts_current": c_counts.tolist()
            }
        except Exception as e:
            logger.error("Failed to compute PSI: %s", e)
            return {"psi_score": 0.0, "drift_status": "error", "detail": str(e)}

    def check_features_drift(
        self,
        reference_data: Dict[str, List[float]],
        production_data: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Evaluate drift across a dictionary of features."""
        results = {}
        for feature_name, current_vals in production_data.items():
            baseline_vals = reference_data.get(feature_name)
            if not baseline_vals:
                continue
                
            ks_res = self.calculate_ks_drift(baseline_vals, current_vals)
            psi_res = self.calculate_psi(baseline_vals, current_vals)
            
            results[feature_name] = {
                "ks_test": ks_res,
                "psi": psi_res,
                "drift_flagged": ks_res["drift_detected"] or (psi_res.get("psi_score", 0.0) >= 0.25)
            }
            
            if results[feature_name]["drift_flagged"]:
                logger.warning(
                    "Feature drift detected in feature '%s'! KS p-val: %.4f, PSI: %.4f",
                    feature_name, ks_res.get("p_value", 1.0), psi_res.get("psi_score", 0.0)
                )
                
        return results
