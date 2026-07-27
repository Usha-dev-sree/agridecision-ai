"""
Unit Tests for AgriDecision AI Core Business Rules
"""
import unittest
from decimal import Decimal


def calculate_water_requirement(eto_mm: float, kc_factor: float) -> float:
    """Calculate crop water requirement ETc = ETo * Kc"""
    if eto_mm < 0 or kc_factor < 0:
        raise ValueError("Invalid negative weather inputs")
    return round(eto_mm * kc_factor, 2)


def validate_soil_ph(ph: float) -> bool:
    """Validate soil pH range (0 to 14)"""
    return 0.0 <= ph <= 14.0


class TestAgriCoreRules(unittest.TestCase):

    def test_water_requirement_calculation(self):
        # ETo = 5.0 mm/day, Kc = 1.15 for peak Maize growth stage
        result = calculate_water_requirement(5.0, 1.15)
        self.assertEqual(result, 5.75)

    def test_water_requirement_negative_input(self):
        with self.assertRaises(ValueError):
            calculate_water_requirement(-2.0, 1.0)

    def test_soil_ph_valid(self):
        self.assertTrue(validate_soil_ph(6.5))
        self.assertTrue(validate_soil_ph(7.0))
        self.assertTrue(validate_soil_ph(0.0))
        self.assertTrue(validate_soil_ph(14.0))

    def test_soil_ph_invalid(self):
        self.assertFalse(validate_soil_ph(-1.5))
        self.assertFalse(validate_soil_ph(14.5))


if __name__ == '__main__':
    unittest.main()
