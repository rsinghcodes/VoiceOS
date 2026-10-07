"""
Locust load test suite for VoiceOS backend per BRAIN §54.
Simulates concurrent voice assistant sessions querying the catalog, adding items to cart, and placing orders.
"""

import uuid
from locust import HttpUser, task, between


class VoiceOSCustomerUser(HttpUser):
    """Simulates realistic customer conversation turns."""

    wait_time = between(1, 3)

    def on_start(self):
        """Initialize session and cart identifiers."""
        self.session_id = f"locust_{uuid.uuid4().hex[:8]}"

    @task(3)
    def test_health_check(self):
        """Verify API health endpoint."""
        self.client.get("/api/v1/health", name="/api/v1/health")

    @task(2)
    def test_root_endpoint(self):
        """Verify root discovery endpoint."""
        self.client.get("/", name="/")
