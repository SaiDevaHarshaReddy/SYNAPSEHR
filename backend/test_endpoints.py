import asyncio
import httpx
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_all():
    print("Logging in...")
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@synapsehr.com", "password": "Admin@123"}
    )
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
        
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")
    
    endpoints = [
        "/api/v1/employees",
        "/api/v1/recruitment/candidates",
        "/api/v1/analytics/dashboard"
    ]
    
    for ep in endpoints:
        print(f"\nTesting {ep}...")
        try:
            response = client.get(ep, headers=headers)
            print(f"Status: {response.status_code}")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except Exception:
                print(f"Response (text): {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_all()
