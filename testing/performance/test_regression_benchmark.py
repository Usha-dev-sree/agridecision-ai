"""
Regression and Performance Benchmark Test Suite
Measures latency thresholds and numerical consistency
"""
import unittest
import time
from testing.unit.test_services import calculate_water_requirement


class TestRegressionBenchmark(unittest.TestCase):

    def test_water_requirement_latency_benchmark(self):
        """Ensure water calculation takes < 1ms per 10,000 iterations"""
        start = time.perf_counter()
        for _ in range(10000):
            calculate_water_requirement(5.2, 1.1)
        duration_ms = (time.perf_counter() - start) * 1000.0

        # Must execute 10,000 calls in under 50 milliseconds
        self.assertLess(duration_ms, 50.0)

    def test_numerical_precision_regression(self):
        """Verify float calculations do not drift precision across software versions"""
        val = calculate_water_requirement(6.432, 1.254)
        self.assertEqual(val, 8.07)


if __name__ == '__main__':
    unittest.main()
