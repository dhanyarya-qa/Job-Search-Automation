import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_login_flow():
    async with httpx.AsyncClient() as client:
        print("=== Testing Login Flow ===\n")
        
        # Step 1: Request OTP
        username = "Dhany Arya Pratama"
        print(f"1. Requesting OTP for {username}...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"username": username}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}\n")
            
            if response.status_code != 200:
                print("❌ Failed to request OTP")
                return
            
            print("✅ OTP requested successfully")
            
        except Exception as e:
            print(f"❌ Error requesting OTP: {e}")
            return
        
        # Step 2: Get OTP from user
        otp = input("\nEnter the OTP you received: ")
        
        # Step 3: Verify OTP
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
            print(f"Response: {response.json()}\n")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Login successful!")
                print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
            else:
                print("❌ OTP verification failed")
                
        except Exception as e:
            print(f"❌ Error verifying OTP: {e}")

if __name__ == "__main__":
    asyncio.run(test_login_flow())
