"""
Financial Service - Agro-Financial Risk Scoring Engine
"""


class AgroRiskScoringEngine:
    def calculate_credit_score(
        self, area_ha: float, soil_health: float, yield_avg: float
    ) -> tuple[int, str, float, float, list[str]]:
        """
        Compute FICO-like credit score (300-850) based on agronomic stability factors.
        """
        base_score = 550

        # Soil factor (+ up to 120 pts)
        soil_bonus = int((soil_health / 100.0) * 120)

        # Yield factor (+ up to 130 pts)
        yield_bonus = int(min(yield_avg / 3500.0, 1.0) * 130)

        # Area factor (+ up to 50 pts)
        area_bonus = int(min(area_ha / 5.0, 1.0) * 50)

        final_score = min(max(base_score + soil_bonus + yield_bonus + area_bonus, 300), 850)

        if final_score >= 750:
            category = "LOW_RISK"
            interest_rate = 7.5
            max_loan = area_ha * 75000.0
        elif final_score >= 620:
            category = "MODERATE_RISK"
            interest_rate = 9.8
            max_loan = area_ha * 45000.0
        else:
            category = "HIGH_RISK"
            interest_rate = 13.5
            max_loan = area_ha * 20000.0

        drivers = [
            f"Soil Health Score ({soil_health}/100)",
            f"Historical Average Yield ({yield_avg} kg/ha)",
            f"Cultivated Area ({area_ha} Ha)"
        ]

        return final_score, category, round(max_loan, 2), interest_rate, drivers
