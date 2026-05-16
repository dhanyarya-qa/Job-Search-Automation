"""Get Telegram Chat ID"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from telegram import Bot
from app.config import settings

async def main():
    print("🔍 Getting Telegram Chat ID...")
    print(f"📱 Bot Token: {settings.telegram_bot_token[:20]}...")
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Get bot info
        me = await bot.get_me()
        print(f"\n✅ Bot connected successfully!")
        print(f"🤖 Bot Username: @{me.username}")
        print(f"🤖 Bot Name: {me.first_name}")
        
        # Get updates to find chat ID
        print(f"\n📥 Getting recent messages...")
        updates = await bot.get_updates()
        
        if not updates:
            print("\n⚠️  No messages found!")
            print("\n📝 To get your Chat ID:")
            print(f"1. Open Telegram and search for: @{me.username}")
            print(f"2. Click 'START' or send any message to the bot")
            print(f"3. Run this script again")
        else:
            print(f"\n✅ Found {len(updates)} message(s)")
            print("\n📋 Available Chat IDs:")
            for update in updates:
                if update.message:
                    chat = update.message.chat
                    print(f"\n  Chat ID: {chat.id}")
                    print(f"  Type: {chat.type}")
                    if chat.username:
                        print(f"  Username: @{chat.username}")
                    if chat.first_name:
                        print(f"  Name: {chat.first_name}")
            
            # Show the most recent chat ID
            if updates[-1].message:
                latest_chat_id = updates[-1].message.chat.id
                print(f"\n💡 Use this Chat ID in your .env file:")
                print(f"   TELEGRAM_CHAT_ID={latest_chat_id}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check TELEGRAM_BOT_TOKEN is correct")
        print("2. Make sure bot token is valid")
        print("3. Check internet connection")

if __name__ == "__main__":
    asyncio.run(main())
