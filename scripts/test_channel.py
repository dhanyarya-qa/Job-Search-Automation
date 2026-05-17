"""
Test sending message to Telegram Channel
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.notifications.telegram_notifier import TelegramNotifier
from app.config import settings


async def test_channel():
    """Test sending to channel"""
    print("=" * 60)
    print("📱 TESTING TELEGRAM CHANNEL")
    print("=" * 60)
    print()
    
    print(f"Bot Token: {settings.telegram_bot_token[:20]}...")
    print(f"Chat ID: {settings.telegram_chat_id}")
    print(f"Channel ID: {settings.telegram_channel_id or 'NOT SET'}")
    print()
    
    if not settings.telegram_channel_id:
        print("⚠️  TELEGRAM_CHANNEL_ID not set in .env")
        print()
        print("To get your channel ID:")
        print("1. Add bot as admin to channel")
        print("2. Run: python scripts/get_channel_id.py")
        print("3. Or forward channel message to @userinfobot")
        print()
        return
    
    notifier = TelegramNotifier()
    
    # Test message
    test_message = """
🧪 <b>Test Message</b>

This is a test message to verify:
✅ Bot can send to personal chat
✅ Bot can send to channel

If you see this in both places, it's working! 🎉
"""
    
    print("📤 Sending test message...")
    success = await notifier.send_message(test_message, to_channel=True)
    
    if success:
        print("✅ Message sent successfully!")
        print()
        print("Check:")
        print(f"1. Your personal chat with bot")
        print(f"2. Your channel: https://t.me/+wchyhkrRqJoyMGM9")
    else:
        print("❌ Failed to send message")
        print()
        print("Troubleshooting:")
        print("- Make sure bot is admin in channel")
        print("- Bot needs 'Post Messages' permission")
        print("- Channel ID format should be: -100xxxxxxxxxx")


if __name__ == "__main__":
    asyncio.run(test_channel())
