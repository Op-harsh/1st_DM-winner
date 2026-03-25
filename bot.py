import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
STRING_SESSION = os.environ.get("STRING_SESSION", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userbot = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

IST = pytz.timezone('Asia/Kolkata')

async def snipe_message(target_entity, message, target_time):
    now = datetime.now(IST)
    delay = (target_time - now).total_seconds()
    adjusted_delay = delay - 0.05  # 0.05s Prefire
    
    if adjusted_delay > 0:
        print(f"Sone ja raha hu. {adjusted_delay} seconds baad message fire hoga!")
        await asyncio.sleep(adjusted_delay)
    
    try:
        # Ab hum direct resolved entity bhej rahe hain, no error chances
        await userbot.send_message(target_entity, message)
        await bot.send_message(ADMIN_ID, f"✅ Mission successful! Message bhej diya gaya top speed me.")
    except Exception as e:
        await bot.send_message(ADMIN_ID, f"❌ End moment pe error aa gaya: {str(e)}")

@bot.on(events.NewMessage(pattern='/start', chats=ADMIN_ID))
async def start_handler(event):
    await event.reply("Jarvis ready hai bhai. Command de: `/snipe`")

@bot.on(events.NewMessage(pattern='/snipe', chats=ADMIN_ID))
async def snipe_handler(event):
    async with bot.conversation(event.chat_id) as conv:
        try:
            await conv.send_message("🎯 Kisko bhejna hai? (Username de, jaise `@username`):")
            target_response = await conv.get_response()
            raw_target = target_response.text.strip()

            await conv.send_message("🔍 Target verify kar raha hu, 2 second ruk...")
            
            # Yahan hum entity resolve kar rahe hain
            try:
                # Agar galti se id (number) daal diya, toh int me convert kar dega
                if raw_target.lstrip('-').isdigit():
                    raw_target = int(raw_target)
                
                target_entity = await userbot.get_entity(raw_target)
                target_name = target_entity.username or target_entity.first_name or str(raw_target)
                await conv.send_message(f"✅ Target mil gaya: {target_name}")
            except Exception as e:
                await conv.send_message(f"❌ Target nahi mila bhai! Sahi username daal.\nError: `{str(e)}`")
                return

            await conv.send_message("📝 Kya message bhejna hai?:")
            msg_response = await conv.get_response()
            message = msg_response.text

            await conv.send_message("⏰ Time bata IST mein.\nFormat ekdum yahi rakhna: `YYYY-MM-DD HH:MM:SS`\nExample: `2026-03-25 18:30:00`")
            time_response = await conv.get_response()
            time_str = time_response.text

            try:
                target_time = IST.localize(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                await conv.send_message("❌ Time ka format galat hai bhai. Script cancel. Wapas `/snipe` type kar.")
                return

            await conv.send_message(f"🔥 Done! Message scheduled.\nTarget: {target_name}\nTime: {time_str} (IST)\n0.05s Prefire active hai.")
            
            # Snipe function me ab username ki jagah 'target_entity' bhej rahe hain
            asyncio.create_task(snipe_message(target_entity, message, target_time))

        except Exception as e:
            await conv.send_message(f"❌ Kuch gadbad ho gayi: {str(e)}")

async def main():
    await userbot.start()
    print("Userbot (Farzi ID) logged in!")
    print("Bot is listening for commands...")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
