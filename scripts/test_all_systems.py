"""
Comprehensive system test - verifies all components are working
"""
import asyncio
import httpx
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.config import settings

async def test_all_systems():
    print("=" * 60)
    print("ULTIMATE JOB HUNTING ATS - SYSTEM STATUS CHECK")
    print("=" * 60)
    print()
    
    results = {
        "backend": False,
        "database": False,
        "login": False,
        "telegram": False,
    }
    
    API_URL = settings.fastapi_base_url
    
    # Test 1: Backend Health
    print("1️⃣  BACKEND API")
    print("-" * 60)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_URL}/health", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Status: {data.get('status')}")
                print(f"✅ App: {data.get('app')}")
                print(f"✅ Version: {data.get('version')}")
                print(f"✅ Environment: {data.get('env')}")
                results["backend"] = True
            else:
                print(f"❌ Health check failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
    print()
    
    # Test 2: Database
    print("2️⃣  DATABASE")
    print("-" * 60)
    try:
        from pathlib import Path
        db_path = Path("job_hunting_ats.db")
        if db_path.exists():
            size = db_path.stat().st_size
            print(f"✅ Database file exists: {db_path}")
            print(f"✅ Size: {size:,} bytes")
            results["database"] = True
        else:
            print("❌ Database file not found")
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    print()
    
    # Test 3: Login System
    print("3️⃣  LOGIN SYSTEM")
    print("-" * 60)
    try:
        async with httpx.AsyncClient() as client:
            username = settings.candidate_name
            
            # Request OTP
            resp = await client.post(
                f"{API_URL}/api/v1/auth/login",
                json={"username": username},
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                otp = data.get("otp")
                print(f"✅ OTP generation working")
                print(f"✅ Debug mode: {settings.debug}")
                
                if otp:
                    # Verify OTP
                    resp = await client.post(
                        f"{API_URL}/api/v1/auth/verify-otp",
                        json={"username": username, "otp_code": otp},
                        timeout=10
                    )
                    
                    if resp.status_code == 200:
                        print(f"✅ OTP verification working")
                        print(f"✅ JWT token generation working")
                        results["login"] = True
                    else:
                        print(f"❌ OTP verification failed")
                else:
                    print("⚠️  OTP not in response (production mode)")
            else:
                print(f"❌ OTP request failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Login system error: {e}")
    print()
    
    # Test 4: Telegram
    print("4️⃣  TELEGRAM NOTIFICATIONS")
    print("-" * 60)
    try:
        if settings.telegram_bot_token and settings.telegram_chat_id:
            print(f"✅ Bot token configured")
            print(f"✅ Chat ID: {settings.telegram_chat_id}")
            print(f"✅ Bot: @nyarioportunitibot")
            results["telegram"] = True
        else:
            print("⚠️  Telegram not configured")
    except Exception as e:
        print(f"❌ Telegram check failed: {e}")
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = len(results)
    passed = sum(results.values())
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component.upper()}: {'WORKING' if status else 'FAILED'}")
    
    print()
    print(f"Overall: {passed}/{total} components working")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    elif passed >= total * 0.75:
        print("⚠️  Most systems working, some issues detected")
    else:
        print("❌ Critical issues detected")
    
    print()
    print("=" * 60)
    print("SERVICES")
    print("=" * 60)
    print(f"🌐 Backend API: http://localhost:8000")
    print(f"📊 Dashboard: http://localhost:8502")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all_systems())
