import random
from locust import HttpUser, task, between


class AegisUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Register and log in once when this simulated user starts."""
        username = f"loadtest_user_{random.randint(1, 100000)}"
        self.user_data = {
            "username": username,
            "password": "loadtestpass123",
            "role": "doctor",
            "wallet_address": None,
        }
        self.client.post("/register", json=self.user_data)
        login_response = self.client.post("/login", json=self.user_data)
        self.token = login_response.json().get("access_token", "")

    @task
    def query_endpoint(self):
        self.client.post(
            "/query",
            json={"question": "What symptoms did the patient have?"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
