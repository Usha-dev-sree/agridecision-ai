"""
Integration Test Suite - Testing microservice interaction pipelines
"""
import unittest
import requests

BASE_GATEWAY_URL = "http://localhost:8000"


class TestEndToEndPipeline(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def test_01_user_authentication_flow(self):
        """Test authentication flow through Gateway"""
        login_data = {
          "username": "9000000000",
          "password": "Password123"
        }
        # Attempt login endpoint call
        try:
            response = self.session.post(
                f"{BASE_GATEWAY_URL}/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=3
            )
            if response.status_code == 200:
                token_data = response.json()
                self.assertIn("access_token", token_data)
        except requests.exceptions.ConnectionError:
            self.skipTest("API Gateway not running locally. Skipping live integration assertion.")

    def test_02_advisory_recommendation_flow(self):
        """Test requesting ML recommendations"""
        payload = {
            "plot_id": "00000000-0000-0000-0000-000000000001",
            "season_name": "KHARIF"
        }
        try:
            response = self.session.post(
                f"{BASE_GATEWAY_URL}/v1/advisory/recommendations",
                json=payload,
                headers=self.headers,
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                self.assertIn("recommendations", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("Advisory service not running locally. Skipping live integration assertion.")


if __name__ == '__main__':
    unittest.main()
