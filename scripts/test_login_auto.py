import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_login_flow():
    async with httpx.AsyncClient() as client:
        print("=== Testing Complete Login Flow ===\n")
        
        username = "Dhany Arya Pratama"
        
        # Step 1: Request OTP
        print(f"1. Requesting OTP for {username}...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"username": username}
            )
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {data}\n")
            
            if response.status_code != 200:
                print("❌ Failed to request OTP")
                return
            
            otp = data.get("otp")
            if not otp:
                print("❌ No OTP in response (debug mode not enabled?)")
                return
                
            print(f"✅ OTP generated: {otp}")
            
        except Exception as e:
            print(f"❌ Error requesting OTP: {e}")
            return
        
        # Step 2: Verify OTP
        print(f"\n2. Verifying OTP: {otp}...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/verify-otp",
                json={
                    "username": username,
                    "otp_code": otp
                }
            )
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response: {data}\n")
            
            if response.status_code == 200:
                print("✅ Login successful!")
                print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
                print(f"Refresh Token: {data.get('refresh_token', 'N/A')[:50]}...")
                print(f"Token Type: {data.get('token_type', 'N/A')}")
                print("\n🎉 Complete login flow working!")
            else:
                print("❌ OTP verification failed")
                
        except Exception as e:
            print(f"❌ Error verifying OTP: {e}")

if __name__ == "__main__":
    asyncio.run(test_login_flow())
