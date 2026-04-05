import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from pymongo import MongoClient

# --- 𝗖𝗢𝗡𝗙𝗜𝗚 ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0")) 
FSUB_ID = int(os.environ.get("FSUB_ID", "0")) 

BYPASS_API_KEY = os.environ.get("BYPASS_API_KEY", "SH4DAW-D4DY")
FORCE_SUB_LINK = "https://t.me/+4hW0nmW34rRjN2Fl"

# --- 𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘 ---
db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']
chats_col = db['chats']

server = Flask(__name__)
@server.route('/')
def status(): return '𝗤𝗨𝗢𝗧𝗘 𝗙𝗘𝗔𝗧𝗨𝗥𝗘 𝗢𝗡𝗟𝗜𝗡𝗘'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 𝗨𝗧𝗜𝗟𝗦 ---
async def check_fsub(client, message):
    if not FSUB_ID: return True
    try:
        await client.get_chat_member(FSUB_ID, message.from_user.id)
        return True
    except UserNotParticipant: return False
    except: return True

# --- 𝗕𝗬𝗣𝗔𝗦𝗦 𝗟𝗢𝗚𝗜𝗖 𝗪𝗜𝗧𝗛 𝗤𝗨𝗢𝗧𝗘 ---
@app.on_message(filters.text & ~filters.command(["start", "stats", "broadcast"]))
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if "http" not in user_link: return

    # Force Join Check
    if not await check_fsub(client, message):
        return await message.reply_text(
            "⚠️ **𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!**\n\n**𝗕𝗬𝗣𝗔𝗦𝗦 𝗞𝗘 𝗟𝗜𝗬𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗝𝗢𝗜𝗡 𝗞𝗔𝗥𝗡𝗔 𝗭𝗔𝗥𝗢𝗢𝗥𝗜 𝗛𝗔𝗜.**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✅𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟✅", url=FORCE_SUB_LINK)
            ]])
        )

    start_time = time.time()
    try: await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="👀")
    except: pass

    # initial processing message
    msg = await message.reply_text("**𝗕𝗬𝗣𝗔𝗦𝗦𝗜𝗡𝗚... ⏳**", quote=True) 

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        res = requests.get(api_url, timeout=30).json()

        if res.get("status"):
            bypassed = res["info"]["bypass"]
            original = res["info"]["original"]
            time_taken = time.time() - start_time
            
            response_text = (
                f"⚡ **𝗔𝗔𝗩𝗬𝗔 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧** ⚡\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"🔗 **𝗢𝗥𝗜𝗚𝗜𝗡𝗔𝗟 𝗟𝗜𝗡𝗞:**\n`{original}`\n\n"
                f"🚀 **𝗕𝗬𝗣𝗔𝗦𝗦𝗘𝗗 𝗟𝗜𝗡𝗞:**\n`{bypassed}`\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⏱️ **𝗧𝗜𝗠𝗘: `{time_taken:.2f}𝗦`**\n"
                f"👩‍💻 **𝗗𝗘𝗩: @rajfflive 🚀**"
            )
            
            try: await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="🔥")
            except: pass
            
            # Final reply with Quote feature
            await msg.edit(response_text, disable_web_page_preview=True)
        else:
            await msg.edit("❌ **𝗔𝗣𝗜 𝗘𝗥𝗥𝗢𝗥! 𝗟𝗜𝗡𝗞 𝗡𝗢𝗧 𝗦𝗨𝗣𝗣𝗢𝗥𝗧𝗘𝗗.**")
            
    except Exception:
        await msg.edit("❌ **𝗦𝗘𝗥𝗩𝗘𝗥 𝗘𝗥𝗥𝗢𝗥!**")

# Start, Stats, aur Broadcast commands pichle code jaise hi rahenge...
# (Baaki code same copy kar lena)

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
