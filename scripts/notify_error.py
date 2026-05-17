"""
Error Notification Script - Send errors to Telegram
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.notifications.telegram_notifier import TelegramNotifier


async def notify_error(module: str, error_message: str, traceback: str = None):
    """Send error notification to Telegram"""
    notifier = TelegramNotifier()
    
    text = f"❌ <b>System Error</b>\n\n"
    text += f"📦 <b>Module:</b> {module}\n"
    text += f"⚠️ <b>Error:</b>\n<code>{error_message[:500]}</code>\n"
    
    if traceback:
        text += f"\n📋 <b>Traceback:</b>\n<code>{traceback[:500]}</code>"
    
    await notifier.send_message(text)
    print(f"✅ Error notification sent to Telegram")


async def main():
    if len(sys.argv) < 3:
        print("Usage: python notify_error.py <module> <error_message> [traceback]")
        print("Example: python notify_error.py 'Job Scraper' 'Connection timeout'")
        return
    
    module = sys.argv[1]
    error_message = sys.argv[2]
    traceback = sys.argv[3] if len(sys.argv) > 3 else None
    
    await notify_error(module, error_message, traceback)


if __name__ == "__main__":
    asyncio.run(main())
