"""
Get Telegram Channel ID from invite link
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Bot
from app.config import settings


async def get_channel_id():
    """Get channel ID by having bot send a test message"""
    print("=" * 60)
    print("📱 TELEGRAM CHANNEL ID FINDER")
    print("=" * 60)
    print()
    
    if not settings.telegram_bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not configured in .env")
        return
    
    print("📋 Instructions:")
    print("1. Add your bot to the channel as admin")
    print("2. Give it 'Post Messages' permission")
    print("3. Send any message to the channel")
    print("4. Run this script")
    print()
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Get bot info
        me = await bot.get_me()
        print(f"✅ Bot connected: @{me.username}")
        print()
        
        # Get updates to find channel ID
        print("🔍 Looking for recent channel messages...")
        updates = await bot.get_updates(limit=100)
        
        channels_found = set()
        
        for update in updates:
            # Check channel posts
            if update.channel_post:
                chat = update.channel_post.chat
                if chat.type == "channel":
                    channels_found.add((chat.id, chat.title))
            
            # Check messages (if bot is in group connected to channel)
            if update.message and update.message.chat.type in ["channel", "supergroup"]:
                chat = update.message.chat
                channels_found.add((chat.id, chat.title))
        
        if channels_found:
            print(f"✅ Found {len(channels_found)} channel(s):")
            print()
            for channel_id, channel_title in channels_found:
                print(f"📢 Channel: {channel_title}")
                print(f"   ID: {channel_id}")
                print(f"   Add to .env: TELEGRAM_CHANNEL_ID={channel_id}")
                print()
        else:
            print("❌ No channels found in recent updates")
            print()
            print("💡 Try this:")
            print("1. Make sure bot is admin in channel")
            print("2. Post a message in the channel")
            print("3. Run this script again")
            print()
            print("Or use @userinfobot:")
            print("1. Forward a message from your channel to @userinfobot")
            print("2. It will show you the channel ID")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure:")
        print("- Bot token is correct")
        print("- Bot is added as admin to channel")
        print("- Bot has 'Post Messages' permission")


if __name__ == "__main__":
    asyncio.run(get_channel_id())
