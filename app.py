import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from pymongo import MongoClient

# --- CONFIG (RENDER SETTINGS SE UTHAYEGA) ---
# Saare ID ko int() mein wrap kiya hai crash se bachne ke liye
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0")) 
FSUB_ID = int(os.environ.get("FSUB_ID", "0")) 

BYPASS_API_KEY = os.environ.get("BYPASS_API_KEY", "SH4DAW-D4DY")
FORCE_SUB_LINK = "https://t.me/+4hW0nmW34rRjN2Fl"

# --- DATABASE ---
try:
    db_client = MongoClient(MONGO_URL)
    db = db_client['BypassBotDB']
    users_col = db['users']
    chats_col = db['chats']
except Exception as e:
    print(f"DATABASE ERROR: {e}")

# --- FLASK FOR RENDER ---
server = Flask(__name__)
@server.route('/')
def status(): return 'BOT IS RUNNING'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- FSUB CHECK ---
async def check_fsub(client, message):
    if not FSUB_ID: return True
    try:
        await client.get_chat_member(FSUB_ID, message.from_user.id)
        return True
    except UserNotParticipant: return False
    except: return True

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    is_joined = await check_fsub(client, message)
    buttons = []
    if not is_joined:
        buttons.append([InlineKeyboardButton("✅𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟✅", url=FORCE_SUB_LINK)])
    
    buttons.append([InlineKeyboardButton("🎀𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗚𝗥𝗢𝗨𝗣🎀", url=f"http://t.me/{app.me.username}?startgroup=true")])
    buttons.append([InlineKeyboardButton("🚀𝗕𝗨𝗬 𝗔𝗣𝗜🚀", url="https://t.me/rajfflive")])

    text = f"👋 **𝗛𝗘𝗟𝗟𝗢 @{message.from_user.username} !!**\n\n**𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗔𝗔𝗩𝗬𝗔 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧 !**"
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- BYPASS HANDLER ---
@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    if message.text.startswith("/"): return
    if not await check_fsub(client, message):
        return await message.reply_text("❌ **𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗙𝗜𝗥𝗦𝗧!**", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ **𝗝𝗢𝗜𝗡**", url=FORCE_SUB_LINK)]]))

    user_link = message.text.strip()
    if not user_link.startswith("http"): return

    start_time = time.time()
    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("**𝗕𝗬𝗣𝗔𝗦𝗦𝗜𝗡𝗚... ⏳**")

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        res = requests.get(api_url, timeout=30).json()
        if res.get("status"):
            bypassed = res["info"]["bypass"]
            time_taken = time.time() - start_time
            response = f"⚡ **𝗕𝗬𝗣𝗔𝗦𝗦𝗘𝗗:**\n> {bypassed}\n\n⏱️ **𝗧𝗜𝗠𝗘: `{time_taken:.2f}𝗦`**\n👩‍💻 **𝗗𝗘𝗩: @rajfflive**"
            await msg.edit(response, disable_web_page_preview=True)
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
        else: await msg.edit("❌ **𝗔𝗣𝗜 𝗘𝗥𝗥𝗢𝗥!**")
    except: await msg.edit("❌ **𝗘𝗥𝗥𝗢𝗥!**")

if __name__ == "__main__":
    from threading import Thread
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: server.run(host="0.0.0.0", port=port)).start()
    app.run()
