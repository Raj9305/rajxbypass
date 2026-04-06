import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pymongo import MongoClient

# ==================== YOUR SETTINGS (EDIT THESE) ====================
API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))   # Your Telegram user ID
BYPASS_API_KEY = os.environ.get("BYPASS_API_KEY", "SH4DAW-D4DY")

# ========== FORCE SUBSCRIBE (UPDATE WITH CORRECT ID & LINK) ==========
FSUB_ID = -1003898508261               # <--- UPDATE with ID from @userinfobot
FORCE_SUB_LINK = "https://t.me/+HpoHOHMq0VpiYWVl"   # Your invite link
# =====================================================================

db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']
groups_col = db['groups']
banned_col = db['banned']

server = Flask(__name__)
@server.route('/')
def status():
    return "Bot alive"

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def add_user(user_id, name="", username=""):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id, "name": name, "username": username})

def add_group(chat_id, title=""):
    if not groups_col.find_one({"chat_id": chat_id}):
        groups_col.insert_one({"chat_id": chat_id, "title": title})

def is_banned(user_id):
    return banned_col.find_one({"user_id": user_id}) is not None

async def is_member(client, user_id):
    """Check if user is in the channel. Returns True if yes, False otherwise."""
    try:
        member = await client.get_chat_member(FSUB_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except UserNotParticipant:
        return False
    except ChatAdminRequired:
        # Bot is not admin – notify the owner
        await client.send_message(ADMIN_ID, f"⚠️ **BOT IS NOT ADMIN** in the force-sub channel!\nChannel ID: `{FSUB_ID}`\nPlease add bot as admin with 'Get Members' permission.")
        return False
    except Exception:
        return False

async def force_sub_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=FORCE_SUB_LINK)],
        [InlineKeyboardButton("🔄 I've Joined", callback_data="check")]
    ])

@app.on_callback_query()
async def callback(client, query):
    if query.data == "check":
        if await is_member(client, query.from_user.id):
            await query.answer("✅ Access granted! You can use the bot.", show_alert=True)
            await query.message.edit(
                "✨ **Access Granted!**\nSend me any short link.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ ADD TO GROUP", url=f"http://t.me/{app.me.username}?startgroup=true")]
                ])
            )
        else:
            await query.answer("❌ You still haven't joined. Please join first.", show_alert=True)

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    add_user(user_id, message.from_user.first_name, message.from_user.username)
    if is_banned(user_id):
        return await message.reply_text("🚫 Banned.", quote=True)
    if not await is_member(client, user_id):
        await message.reply_text(
            f"👋 **Hello {message.from_user.first_name}!**\n\n"
            "⚠️ **You must join our channel to use this bot.**\n"
            "Click below, join, then press **I've Joined**.",
            reply_markup=await force_sub_keyboard(),
            quote=True
        )
        return
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD TO GROUP", url=f"http://t.me/{app.me.username}?startgroup=true")],
        [InlineKeyboardButton("ℹ️ HELP", callback_data="help"), InlineKeyboardButton("📊 STATS", callback_data="stats")]
    ])
    await message.reply_text(
        f"✨ **Welcome {message.from_user.first_name}!**\nSend me any short link.",
        reply_markup=buttons,
        quote=True
    )

@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    if is_banned(message.from_user.id):
        return await message.reply_text("🚫 Banned.", quote=True)
    if not await is_member(client, message.from_user.id):
        return await message.reply_text("⚠️ Join first.", reply_markup=await force_sub_keyboard(), quote=True)
    await message.reply_text("Send any shortlink – I will bypass it.", quote=True)

@app.on_message(filters.text & ~filters.command(["start", "help"]) & filters.private)
async def bypass_private(client, message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return await message.reply_text("🚫 Banned.", quote=True)
    if "http" not in message.text:
        return
    if not await is_member(client, user_id):
        return await message.reply_text("⚠️ Join channel first.", reply_markup=await force_sub_keyboard(), quote=True)
    # Process bypass (same as before)
    msg = await message.reply_text("🔍 Processing...", quote=True)
    try:
        api = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={message.text}"
        res = requests.get(api, timeout=30).json()
        if res.get("status"):
            bypassed = res["info"]["bypass"]
            original = res["info"]["original"]
            await msg.edit(f"✅ **Bypassed!**\n\nOriginal: {original}\nBypassed: {bypassed}", disable_web_page_preview=False)
        else:
            await msg.edit("❌ Bypass failed.")
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

@app.on_message(filters.command("debug") & filters.user(ADMIN_ID))
async def debug(client, message):
    """Check bot admin status and user membership."""
    await message.reply_text(f"🔍 **Debug**\nChannel ID: `{FSUB_ID}`", quote=True)
    # Check bot
    try:
        me = await client.get_me()
        bot_member = await client.get_chat_member(FSUB_ID, me.id)
        await message.reply_text(f"✅ Bot status: `{bot_member.status}`", quote=True)
    except ChatAdminRequired:
        await message.reply_text("❌ **Bot is NOT admin** in the channel!\nAdd bot as admin with 'Get Members' permission.", quote=True)
        return
    except Exception as e:
        await message.reply_text(f"❌ Bot error: {e}", quote=True)
        return
    # Check user
    try:
        member = await client.get_chat_member(FSUB_ID, message.from_user.id)
        await message.reply_text(f"✅ Your status: `{member.status}`\nYou ARE a member.", quote=True)
    except UserNotParticipant:
        await message.reply_text("❌ You are NOT a member of the channel.", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}", quote=True)

if __name__ == "__main__":
    from threading import Thread
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: server.run(host="0.0.0.0", port=port)).start()
    print("Bot started. Send /debug to check force-sub status.")
    app.run()
