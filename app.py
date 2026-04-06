import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from pymongo import MongoClient

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0")) 
FSUB_ID = int(os.environ.get("FSUB_ID", "0")) 

BYPASS_API_KEY = os.environ.get("BYPASS_API_KEY", "SH4DAW-D4DY")
# Naya Link Update Kar Diya
FORCE_SUB_LINK = "http://t.me/+gD6eD6JN3G42OTM9"

# --- DATABASE ---
db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']
chats_col = db['chats']

server = Flask(__name__)
@server.route('/')
def status(): return 'ULTRA CLEAN UI ALIVE'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- UTILS ---
async def check_fsub(client, message):
    if not FSUB_ID: return True
    try:
        await client.get_chat_member(FSUB_ID, message.from_user.id)
        return True
    except UserNotParticipant: return False
    except: return True

def add_serve(chat_id, is_group=False):
    col = chats_col if is_group else users_col
    key = "chat_id" if is_group else "user_id"
    if not col.find_one({key: chat_id}):
        col.insert_one({key: chat_id})

# --- START COMMAND (CLEAN UI) ---
@app.on_message(filters.command("start"))
async def start(client, message):
    add_serve(message.chat.id, is_group=(message.chat.type != "private"))
    is_joined = await check_fsub(client, message)
    
    buttons = []
    # Button 1: Force Join (Agar Joined nahi hai toh)
    if not is_joined:
        buttons.append([InlineKeyboardButton("📢 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url=FORCE_SUB_LINK)])
    
    # Button 2: Add to Group
    buttons.append([InlineKeyboardButton("➕ 𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗬𝗢𝗨𝗥 𝗚𝗥𝗢𝗨𝗣", url=f"http://t.me/{app.me.username}?startgroup=true")])

    welcome_text = (
        f"✨ **𝗛𝗲𝗹𝗹𝗼 {message.from_user.first_name} !**\n\n"
        f"Welcome to **Aavya Bypass Bot**. I can bypass almost any shortlink with lightning speed.\n\n"
        f"🚀 **Status:** `Running Online` 🟢\n"
        f"📂 **Service:** `Link Bypasser`"
    )
    
    await message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(buttons))

# --- BYPASS LOGIC (PREMIUM RESPONSE) ---
@app.on_message(filters.text & ~filters.command(["start", "stats", "broadcast"]))
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if "http" not in user_link: return

    # Force Join Check
    if not await check_fsub(client, message):
        return await message.reply_text(
            "⚠️ **Access Denied!**\n\nPlease join our channel first to use this bot.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=FORCE_SUB_LINK)]]),
            quote=True
        )

    start_time = time.time()
    try: await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="👀")
    except: pass

    msg = await message.reply_text("🔍 **Processing your link...**", quote=True)

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        res = requests.get(api_url, timeout=30).json()

        if res.get("status"):
            bypassed = res["info"]["bypass"]
            original = res["info"]["original"]
            time_taken = time.time() - start_time
            
            response_text = (
                f"✅ **𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗕𝘆𝗽𝗮𝘀𝘀𝗲𝗱 !**\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"🔗 **𝗢𝗿𝗶𝗴𝗶𝗻𝗮𝗹 𝗟𝗶𝗻𝗸:**\n`{original}`\n\n"
                f"🚀 **𝗕𝘆𝗽𝗮𝘀𝘀𝗲𝗱 𝗟𝗶𝗻𝗸:**\n`{bypassed}`\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⏱️ **𝗧𝗶𝗺𝗲:** `{time_taken:.2f}s` | 👤 **𝗕𝘆:** @{message.from_user.username or 'User'}\n"
                f"👩‍💻 **𝗗𝗲𝘃:** @AAVYAXBOTS"
            )
            
            try: await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="🔥")
            except: pass
            
            await msg.edit(response_text, disable_web_page_preview=True)
        else:
            await msg.edit("❌ **Bypass Failed!** Link not supported or API issue.")
            
    except Exception:
        await msg.edit("❌ **Error:** Connection lost with API server.")

# --- ADMIN COMMANDS ---
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats(client, message):
    u_count = users_col.count_documents({})
    c_count = chats_col.count_documents({})
    await message.reply_text(f"📊 **Bot Stats**\n\n👤 Users: `{u_count}`\n👥 Groups: `{c_count}`")

if __name__ == "__main__":
    from threading import Thread
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: server.run(host="0.0.0.0", port=port)).start()
    app.run()
