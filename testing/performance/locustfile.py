"""
Locust Performance and Load Testing Script
Simulates concurrent farmers and agronomists querying APIs
"""
from locust import HttpUser, task, between
import random


class AgriUserBehavior(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_plots(self):
        self.client.get("/v1/plots", name="GET /v1/plots")

    @task(2)
    def check_weather_forecast(self):
        lat = 21.1702 + random.uniform(-0.1, 0.1)
        lon = 72.8311 + random.uniform(-0.1, 0.1)
        self.client.get(f"/v1/weather/forecast?lat={lat}&lon={lon}", name="GET /v1/weather/forecast")

    @task(1)
    def request_crop_recommendation(self):
        payload = {
            "plot_id": "00000000-0000-0000-0000-000000000001",
            "season_name": "KHARIF"
        }
        self.client.post("/v1/advisory/recommendations", json=payload, name="POST /v1/advisory/recommendations")
