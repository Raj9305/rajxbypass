import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from pymongo import MongoClient

# --- 𝗖𝗢𝗡𝗙𝗜𝗚 ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0)) 

BYPASS_API_KEY = os.environ.get("BYPASS_API_KEY", "SH4DAW-D4DY")
FORCE_SUB_LINK = "https://t.me/+4hW0nmW34rRjN2Fl"
FSUB_ID = os.environ.get("FSUB_ID", "") # Render mein numeric ID (-100xxx) zaroor daalna

# --- 𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘 ---
db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']
chats_col = db['chats']

server = Flask(__name__)
@server.route('/')
def status(): return '𝗦𝗧𝗔𝗥𝗧 𝗕𝗨𝗧𝗧𝗢𝗡 𝗙𝗜𝗫𝗘𝗗'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 𝗨𝗧𝗜𝗟𝗦 ---
def add_serve(chat_id, is_group=False):
    col = chats_col if is_group else users_col
    key = "chat_id" if is_group else "user_id"
    if not col.find_one({key: chat_id}):
        col.insert_one({key: chat_id})

async def check_fsub(client, message):
    if not FSUB_ID: return True
    try:
        await client.get_chat_member(FSUB_ID, message.from_user.id)
        return True
    except UserNotParticipant:
        return False
    except: return True

# --- 𝗠𝗔𝗜𝗡 𝗟𝗢𝗚𝗜𝗖 ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    add_serve(message.from_user.id)
    is_joined = await check_fsub(client, message)
    
    # Buttons prepare kar rahe hain
    buttons = []
    
    # ⚠️ Agar join nahi hai toh join button sabse upar
    if not is_joined:
        buttons.append([InlineKeyboardButton("✅𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟✅", url=FORCE_SUB_LINK)])
    
    # Baaki buttons normal
    buttons.append([InlineKeyboardButton("✅𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗚𝗥𝗢𝗨𝗣✅", url=f"http://t.me/{app.me.username}?startgroup=true")])
    buttons.append([InlineKeyboardButton("🚀𝗕𝗨𝗬 𝗔𝗣𝗜", url="https://t.me/rajfflive")])

    welcome_text = (
        f"👋 **𝗛𝗘𝗟𝗟𝗢 @{message.from_user.username} !!**\n\n"
        f"**𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗔𝗔𝗩𝗬𝗔 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧 !**\n\n"
    )
    
    if not is_joined:
        welcome_text += "⚠️ **𝗣𝗟𝗘𝗔𝗦𝗘 𝗝𝗢𝗜𝗡 𝗢𝗨𝗥 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗧𝗢 𝗨𝗦𝗘 𝗠𝗘!**"
    else:
        welcome_text += "**𝗝𝗨𝗦𝗧 𝗦𝗘𝗡𝗗 𝗧𝗛𝗘 𝗟𝗜𝗡𝗞 𝗕𝗘𝗟𝗢𝗪 𝗧𝗢 𝗕𝗬𝗣𝗔𝗦𝗦!**"

    await message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    if message.text.startswith("/"): return
    
    add_serve(message.from_user.id)
    
    # Strict check for bypass
    if not await check_fsub(client, message):
        return await message.reply_text(
            "⚠️ **𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!**\n\n**𝗬𝗢𝗨 𝗠𝗨𝗦𝗧 𝗝𝗢𝗜𝗡 𝗢𝗨𝗥 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗙𝗜𝗥𝗦𝗧!**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ **𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟** ➕", url=FORCE_SUB_LINK)
            ]])
        )

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
            
            response_text = (
                f"⚡ **𝗔𝗔𝗩𝗬𝗔 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧** ⚡\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"🚀 **𝗕𝗬𝗣𝗔𝗦𝗦𝗘𝗗:**\n> {bypassed}\n\n"
                f"⏱️ **𝗧𝗜𝗠𝗘 𝗧𝗔𝗞𝗘𝗡: `{time_taken:.2f}𝗦`**\n"
                f"👩‍💻 **𝗗𝗘𝗩: @rajfflive ✅**"
            )
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            await msg.edit(response_text, disable_web_page_preview=True)
        else:
            await msg.edit("❌ **𝗔𝗣𝗜 𝗘𝗥𝗥𝗢𝗥!**")
    except:
        await msg.edit("❌ **𝗦𝗘𝗥𝗩𝗘𝗥 𝗘𝗥𝗥𝗢𝗥!**")

# Admin commands (stats/broadcast) remains same...
