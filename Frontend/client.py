"""
client.py — RetailPulse API Client
Structure from FRONTEND_DESIGN_SYSTEM.md Section 15.
Endpoints from RETAILPULSE_FRONTEND.md.
"""
import requests
import pandas as pd
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetailPulseClient:

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _make_request(self, endpoint: str, method: str = "GET", json=None) -> Optional[requests.Response]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method, url=url, json=json, timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Failed to connect to API at {url}. Is the backend running?"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Request to {url} timed out after {self.timeout} seconds"
            )
        except requests.exceptions.HTTPError:
            self._handle_error(response)
        except Exception as e:
            raise Exception(f"Unexpected error occurred: {str(e)}")

    def _handle_error(self, response: requests.Response) -> None:
        status_code = response.status_code
        if status_code == 400:
            raise ValueError(f"Bad request: {response.text}")
        elif status_code == 401:
            raise PermissionError(f"401 Unauthorized: {response.text}")
        elif status_code == 403:
            raise PermissionError(f"403 Forbidden: {response.text}")
        elif status_code == 404:
            raise FileNotFoundError(f"404 Resource not found: {response.url}")
        elif status_code == 500:
            raise Exception(f"500 Server error: {response.text}")
        else:
            raise Exception(f"HTTP {status_code}: {response.text}")

    def check_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code < 500
        except Exception:
            return False

    # ── AUTH ──────────────────────────────────────────────────────────────────

    def signup(self, username: str, email: str, password: str) -> dict:
        """POST /auth/signup"""
        try:
            response = self._make_request(
                "/auth/signup",
                method="POST",
                json={"username": username, "email": email, "password": password},
            )
            return response.json()
        except Exception as e:
            logger.error(f"signup failed: {e}")
            raise

    def signin(self, username: str, password: str) -> dict:
        """POST /auth/signin"""
        try:
            response = self._make_request(
                "/auth/signin",
                method="POST",
                json={"username": username, "password": password},
            )
            return response.json()
        except Exception as e:
            logger.error(f"signin failed: {e}")
            raise

    # ── PIPELINE ──────────────────────────────────────────────────────────────

    def run_pipeline(self) -> dict:
        """POST /run-pipeline"""
        try:
            response = self._make_request("/run-pipeline", method="POST")
            return response.json()
        except Exception as e:
            logger.error(f"run_pipeline failed: {e}")
            raise

    def get_pipeline_status(self) -> dict:
        """GET /pipeline-status"""
        try:
            response = self._make_request("/pipeline-status")
            return response.json()
        except Exception as e:
            logger.error(f"get_pipeline_status failed: {e}")
            raise

    # ── DATA ENDPOINTS ────────────────────────────────────────────────────────

    def get_stores(self) -> list:
        """GET /stores"""
        try:
            response = self._make_request("/stores")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_stores failed: {e}")
            raise

    def get_products(self) -> list:
        """GET /products"""
        try:
            response = self._make_request("/products")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_products failed: {e}")
            raise

    def get_customers(self) -> list:
        """GET /customers"""
        try:
            response = self._make_request("/customers")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_customers failed: {e}")
            raise

    def get_sales_header(self) -> list:
        """GET /sales-header"""
        try:
            response = self._make_request("/sales-header")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_sales_header failed: {e}")
            raise

    def get_sales_line_items(self) -> list:
        """GET /sales-line-items"""
        try:
            response = self._make_request("/sales-line-items")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_sales_line_items failed: {e}")
            raise

    def get_rfm_summary(self) -> list:
        """GET /rfm-summary"""
        try:
            response = self._make_request("/rfm-summary")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_rfm_summary failed: {e}")
            raise

    def get_customer_predictions(self) -> list:
        """GET /customer-predictions"""
        try:
            response = self._make_request("/customer-predictions")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_customer_predictions failed: {e}")
            raise

    def get_rejected(self, table_name: str) -> list:
        """GET /rejected/{table_name}"""
        try:
            response = self._make_request(f"/rejected/{table_name}")
            data = response.json()
            return data if data else []
        except Exception as e:
            logger.error(f"get_rejected({table_name}) failed: {e}")
            raise

    def get_visualization(self, filename: str) -> bytes:
        """GET /visualizations/{filename} — returns image bytes"""
        try:
            response = self._make_request(f"/visualizations/{filename}")
            return response.content
        except Exception as e:
            logger.error(f"get_visualization({filename}) failed: {e}")
            raise
