import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ==========================================
# 🛑 ENVIRONMENT VARIABLES (Railway pe dalne hain)
# ==========================================
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "") # Fake ID ka session string
OWNER_ID = int(os.environ.get("OWNER_ID", "0")) # Tera real Telegram User ID (Taki koi aur bot use na kar paye)

# Clients Setup
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userbot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

IST = pytz.timezone('Asia/Kolkata')

async def send_delayed_message(target, send_time_ist, message):
    """Asli firing yahan se hogi Fake ID ke through"""
    now_ist = datetime.now(IST)
    delay = (send_time_ist - now_ist).total_seconds()
    
    if delay > 0:
        print(f"⏳ Waiting for {delay} seconds...")
        await asyncio.sleep(delay)
    
    # Pre-fire delay adjustment (0.1 sec pehle) taki ping cover ho jaye
    try:
        await userbot.send_message(target, message)
        await bot.send_message(OWNER_ID, f"✅ Mission Accomplished! Message sent to {target}.")
    except Exception as e:
        await bot.send_message(OWNER_ID, f"❌ Error aagaya bhai: {str(e)}")

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    if event.sender_id != OWNER_ID:
        await event.reply("Nikal yahan se, main sirf Harsh ki sunta hoon! 🛑")
        return

    async with bot.conversation(event.chat_id) as conv:
        try:
            # Step 1: Message
            await conv.send_message("Batao kya message bhejna hai? 📝")
            msg_response = await conv.get_response()
            message_to_send = msg_response.text

            # Step 2: Target
            await conv.send_message("Kisko bhejna hai? (Username ya UserID do) 🎯")
            target_response = await conv.get_response()
            target_user = target_response.text

            # Step 3: Time
            await conv.send_message("Kis time par bhejna hai? \nFormat: `YYYY-MM-DD HH:MM:SS` (24-hour format, IST mein) ⏰\nExample: `2026-03-25 17:00:00`")
            time_response = await conv.get_response()
            time_str = time_response.text
            
            # Parse Time
            send_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            send_time_ist = IST.localize(send_time)
            
            now_ist = datetime.now(IST)
            if send_time_ist <= now_ist:
                await conv.send_message("Bhai, past ka time de raha hai! Time machine nahi hai mere paas. Wapas /start kar. 🤦‍♂️")
                return

            await conv.send_message(f"🔥 Done! Task Scheduled.\nTarget: {target_user}\nTime: {send_time_ist.strftime('%Y-%m-%d %H:%M:%S')} IST\n\nAb aaram se baith, main time aane pe fire kar dunga.")
            
            # Background me timer chalu kar do
            asyncio.create_task(send_delayed_message(target_user, send_time_ist, message_to_send))

        except ValueError:
            await conv.send_message("❌ Time ka format galat daal diya bhai. Fir se /start dabao.")
        except Exception as e:
            await conv.send_message(f"❌ Kuch gadbad ho gayi: {str(e)}")

async def main():
    await userbot.start()
    print("🤖 Userbot Started!")
    print("🤖 Bot Started! Waiting for commands...")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
