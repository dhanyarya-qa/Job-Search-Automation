import httpx
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.config import settings

def test_dashboard_connection():
    print("=== Testing Dashboard Connection to Backend ===\n")
    
    API_URL = settings.fastapi_base_url
    print(f"Backend URL: {API_URL}")
    print(f"Debug Mode: {settings.debug}\n")
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        resp = httpx.get(f"{API_URL}/health", timeout=5)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        print("✅ Health check passed\n")
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")
        return
    
    # Test 2: Login flow
    print("2. Testing login flow...")
    username = settings.candidate_name
    print(f"Username: {username}")
    
    try:
        # Request OTP
        resp = httpx.post(
            f"{API_URL}/api/v1/auth/login",
            json={"username": username},
            timeout=10
        )
        print(f"OTP Request Status: {resp.status_code}")
        data = resp.json()
        print(f"Response: {data}")
        
        if resp.status_code != 200:
            print("❌ OTP request failed\n")
            return
        
        otp = data.get("otp")
        if not otp:
            print("❌ No OTP in response (debug mode not enabled?)\n")
            return
        
        print(f"✅ OTP generated: {otp}\n")
        
        # Verify OTP
        print("3. Testing OTP verification...")
        resp = httpx.post(
            f"{API_URL}/api/v1/auth/verify-otp",
            json={"username": username, "otp_code": otp},
            timeout=10
        )
        print(f"Verify Status: {resp.status_code}")
        data = resp.json()
        
        if resp.status_code == 200:
            print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print("✅ OTP verification passed\n")
            print("🎉 Dashboard can successfully connect to backend!")
        else:
            print(f"❌ OTP verification failed: {data}\n")
            
    except Exception as e:
        print(f"❌ Login flow failed: {e}\n")

if __name__ == "__main__":
    test_dashboard_connection()
