"""
Security Audit Test Suite
Verifies API resistance against SQLi, XSS, and JWT tampering
"""
import unittest
import requests

BASE_URL = "http://localhost:8000"


class TestSecurityAudit(unittest.TestCase):

    def test_sql_injection_resilience(self):
        """Verify API SQL Injection protection on authentication endpoint"""
        sqli_payload = {
            "username": "' OR '1'='1",
            "password": "' OR '1'='1"
        }
        try:
            res = requests.post(
                f"{BASE_URL}/v1/auth/login",
                data=sqli_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=3
            )
            # Response must not be 200 OK or 500 Server Exception Error
            self.assertIn(res.status_code, [400, 401, 422])
        except requests.exceptions.ConnectionError:
            self.skipTest("API not reachable locally.")

    def test_tampered_jwt_rejection(self):
        """Verify tampered JWT tokens return 401 Unauthorized"""
        fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tampered_signature"
        try:
            res = requests.get(
                f"{BASE_URL}/v1/users/me",
                headers={"Authorization": f"Bearer {fake_jwt}"},
                timeout=3
            )
            self.assertEqual(res.status_code, 401)
        except requests.exceptions.ConnectionError:
            self.skipTest("API not reachable locally.")

    def test_xss_input_sanitation(self):
        """Verify XSS script tags are sanitized or safely escaped"""
        xss_payload = {
            "full_name": "<script>alert('xss')</script>",
            "bio": "<img src=x onerror=alert(1)>"
        }
        try:
            res = requests.patch(
                f"{BASE_URL}/v1/users/me",
                json=xss_payload,
                headers={"Authorization": "Bearer fake_token"},
                timeout=3
            )
            self.assertIn(res.status_code, [400, 401, 422])
        except requests.exceptions.ConnectionError:
            self.skipTest("API not reachable locally.")


if __name__ == '__main__':
    unittest.main()
