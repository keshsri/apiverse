import requests
from typing import Optional, Dict, Any
from config import API_BASE_URL

class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        self.token = token
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password, "full_name": full_name}
        )
        response.raise_for_status()
        return response.json()
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data.get("access_token")
        return data
    
    def list_apis(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/apis",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_api(self, name: str, base_url: str, description: str = "", auth_type: str = "none", auth_config: Optional[Dict] = None) -> Dict[str, Any]:
        payload = {
            "name": name,
            "base_url": base_url,
            "description": description,
            "auth_type": auth_type
        }
        if auth_config:
            payload["auth_config"] = auth_config
        
        response = requests.post(
            f"{self.base_url}/apis",
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_api(self, api_id: int, **kwargs) -> Dict[str, Any]:
        response = requests.put(
            f"{self.base_url}/apis/{api_id}",
            json=kwargs,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_api(self, api_id: int):
        response = requests.delete(
            f"{self.base_url}/apis/{api_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
    
    def list_api_keys(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/api-keys",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_api_key(self, name: str, environment: str = "development", expires_in_days: Optional[int] = None) -> Dict[str, Any]:
        payload = {"name": name, "environment": environment}
        if expires_in_days:
            payload["expires_in_days"] = expires_in_days
        
        response = requests.post(
            f"{self.base_url}/api-keys",
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def revoke_api_key(self, key_id: int):
        response = requests.delete(
            f"{self.base_url}/api-keys/{key_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
    
    def get_rate_limit(self, api_id: int) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/rate-limits/{api_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_rate_limit(self, api_id: int, tier: str, requests_per_hour: int, requests_per_day: int) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/rate-limits",
            json={
                "api_id": api_id,
                "tier": tier,
                "requests_per_hour": requests_per_hour,
                "requests_per_day": requests_per_day
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_usage_stats(self, api_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = requests.get(
            f"{self.base_url}/analytics/{api_id}/usage",
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_endpoint_stats(self, api_id: int, limit: int = 10) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/analytics/{api_id}/endpoints",
            params={"limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_error_stats(self, api_id: int) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/analytics/{api_id}/errors",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_performance_stats(self, api_id: int) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/analytics/{api_id}/performance",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def list_webhook_subscriptions(self, api_id: int) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/webhooks/subscriptions",
            params={"api_id": api_id},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_webhook_subscription(self, api_id: int, event_type: str, callback_url: str, secret: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "api_id": api_id,
            "event_type": event_type,
            "callback_url": callback_url,
            "is_active": True
        }
        if secret:
            payload["secret"] = secret
        
        response = requests.post(
            f"{self.base_url}/webhooks/subscriptions",
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_webhook_subscription(self, subscription_id: int):
        response = requests.delete(
            f"{self.base_url}/webhooks/subscriptions/{subscription_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
    
    def get_webhook_deliveries(self, subscription_id: int, limit: int = 50) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/webhooks/subscriptions/{subscription_id}/deliveries",
            params={"limit": limit},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
