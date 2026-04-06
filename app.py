import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient

# -------------------- CONFIG --------------------
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))          # Your Telegram user ID
BYPASS_API_KEY = os.environ.get("BYPASS_API_KEY", "SH4DAW-D4DY")

# Default force-sub values (can be changed via /setfsub and /setlink)
FSUB_ID = int(os.environ.get("FSUB_ID", "0"))
FORCE_SUB_LINK = os.environ.get("FORCE_SUB_LINK", "http://t.me/+gD6eD6JN3G42OTM9")

# -------------------- DATABASE --------------------
db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']          # {user_id, name, username}
groups_col = db['groups']        # {chat_id, title}
banned_col = db['banned']        # {user_id}
settings_col = db['settings']    # {_id: "fsub", fsub_id, fsub_link}

# Load force-sub settings from DB if exist
settings = settings_col.find_one({"_id": "fsub"})
if settings:
    FSUB_ID = settings.get("fsub_id", FSUB_ID)
    FORCE_SUB_LINK = settings.get("fsub_link", FORCE_SUB_LINK)

# -------------------- FLASK SERVER --------------------
server = Flask(__name__)

@server.route('/')
def status():
    return '✅ Bot is alive'

# -------------------- PYROGRAM CLIENT --------------------
app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------------------- HELPER FUNCTIONS --------------------
def add_user(user_id, name="", username=""):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id, "name": name, "username": username})

def add_group(chat_id, title=""):
    if not groups_col.find_one({"chat_id": chat_id}):
        groups_col.insert_one({"chat_id": chat_id, "title": title})

def is_banned(user_id):
    return banned_col.find_one({"user_id": user_id}) is not None

def ban_user(user_id):
    if not is_banned(user_id):
        banned_col.insert_one({"user_id": user_id})

def unban_user(user_id):
    banned_col.delete_one({"user_id": user_id})

async def check_fsub(client, user_id):
    """Return True if user is member of force-sub channel"""
    if not FSUB_ID:
        return True
    try:
        member = await client.get_chat_member(FSUB_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except UserNotParticipant:
        return False
    except Exception:
        return True  # Allow if any error

async def force_sub_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=FORCE_SUB_LINK)],
        [InlineKeyboardButton("🔄 I've Joined", callback_data="check_join")]
    ])

# -------------------- JOIN REQUEST AUTO-APPROVE --------------------
@app.on_chat_join_request(filters.chat(FSUB_ID) if FSUB_ID else filters.chat([]))
async def handle_join_request(client, request):
    try:
        await request.approve()
        await client.send_message(
            request.from_user.id,
            "✅ **You have been approved!**\n\nYou can now use the bot.\nSend me any short link to bypass."
        )
    except Exception as e:
        print(f"Join request error: {e}")

# -------------------- CALLBACK HANDLER (for buttons) --------------------
@app.on_callback_query()
async def callback_handler(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "check_join":
        if await check_fsub(client, user_id):
            await callback_query.answer("✅ You are now a member! You can use the bot.", show_alert=True)
            await callback_query.message.edit(
                "✨ **Access Granted!**\n\nNow send me any short link to bypass.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ ADD TO GROUP", url=f"http://t.me/{app.me.username}?startgroup=true")]
                ])
            )
        else:
            await callback_query.answer("❌ Still not a member. Please join first.", show_alert=True)

    elif data == "help":
        await callback_query.answer("📖 Opening help...")
        await callback_query.message.reply_text(
            "🔍 **How to use me**\n\n"
            "1. Send me any shortlink (e.g., `exe.io`, `shortingly.com`)\n"
            "2. I will process it and give you the direct link.\n"
            "3. Add me to your group – I will work there too.\n\n"
            "**Commands:**\n"
            "/start - Main menu\n"
            "/help - This message",
            quote=True
        )

    elif data == "stats":
        if user_id == ADMIN_ID:
            user_count = users_col.count_documents({})
            group_count = groups_col.count_documents({})
            banned_count = banned_col.count_documents({})
            await callback_query.answer("📊 Fetching stats...")
            await callback_query.message.reply_text(
                f"📊 **Bot Statistics**\n\n"
                f"👤 Users: `{user_count}`\n"
                f"👥 Groups: `{group_count}`\n"
                f"🚫 Banned: `{banned_count}`",
                quote=True
            )
        else:
            await callback_query.answer("⛔ Only bot owner can view stats.", show_alert=True)

# -------------------- OWNER COMMANDS --------------------
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats_cmd(client, message):
    user_count = users_col.count_documents({})
    group_count = groups_col.count_documents({})
    banned_count = banned_col.count_documents({})
    await message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"👤 Users: `{user_count}`\n"
        f"👥 Groups: `{group_count}`\n"
        f"🚫 Banned: `{banned_count}`",
        quote=True
    )

@app.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def users_cmd(client, message):
    users = list(users_col.find({}).limit(10))
    if not users:
        return await message.reply_text("No users found.", quote=True)
    text = "📋 **Recent Users (first 10):**\n\n"
    for u in users:
        text += f"• `{u['user_id']}` – {u.get('name', 'Unknown')}\n"
    await message.reply_text(text, quote=True)

@app.on_message(filters.command("groups") & filters.user(ADMIN_ID))
async def groups_cmd(client, message):
    groups = list(groups_col.find({}).limit(10))
    if not groups:
        return await message.reply_text("No groups found.", quote=True)
    text = "📋 **Recent Groups (first 10):**\n\n"
    for g in groups:
        text += f"• `{g['chat_id']}` – {g.get('title', 'Unknown')}\n"
    await message.reply_text(text, quote=True)

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: `/broadcast Your message here`", quote=True)
    broadcast_text = message.text.split(None, 1)[1]
    users = users_col.find({})
    success = 0
    fail = 0
    status_msg = await message.reply_text("📢 **Broadcasting...** This may take a while.", quote=True)
    for user in users:
        try:
            await client.send_message(user['user_id'], broadcast_text)
            success += 1
            time.sleep(0.05)
        except:
            fail += 1
    await status_msg.edit_text(f"✅ Broadcast finished.\nSent: `{success}`\nFailed: `{fail}`")

@app.on_message(filters.command("ban") & filters.user(ADMIN_ID))
async def ban_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/ban user_id`", quote=True)
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("Invalid user ID.", quote=True)
    ban_user(user_id)
    await message.reply_text(f"✅ User `{user_id}` has been banned.", quote=True)

@app.on_message(filters.command("unban") & filters.user(ADMIN_ID))
async def unban_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/unban user_id`", quote=True)
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("Invalid user ID.", quote=True)
    unban_user(user_id)
    await message.reply_text(f"✅ User `{user_id}` has been unbanned.", quote=True)

@app.on_message(filters.command("leave") & filters.user(ADMIN_ID))
async def leave_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/leave chat_id`", quote=True)
    try:
        chat_id = int(message.command[1])
    except:
        return await message.reply_text("Invalid chat ID.", quote=True)
    try:
        await client.leave_chat(chat_id)
        groups_col.delete_one({"chat_id": chat_id})
        await message.reply_text(f"✅ Left chat `{chat_id}` and removed from DB.", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ Failed: `{e}`", quote=True)

@app.on_message(filters.command("setfsub") & filters.user(ADMIN_ID))
async def set_fsub_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/setfsub channel_id`\nExample: `-1001234567890`", quote=True)
    try:
        fsub_id = int(message.command[1])
    except:
        return await message.reply_text("Invalid ID. Must be integer (e.g., -1001234567890).", quote=True)
    settings_col.update_one({"_id": "fsub"}, {"$set": {"fsub_id": fsub_id}}, upsert=True)
    global FSUB_ID
    FSUB_ID = fsub_id
    await message.reply_text(f"✅ Force-sub channel ID set to `{fsub_id}`.", quote=True)

@app.on_message(filters.command("setlink") & filters.user(ADMIN_ID))
async def set_link_cmd(client, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/setlink invite_link`", quote=True)
    link = message.command[1]
    settings_col.update_one({"_id": "fsub"}, {"$set": {"fsub_link": link}}, upsert=True)
    global FORCE_SUB_LINK
    FORCE_SUB_LINK = link
    await message.reply_text(f"✅ Force-sub link set to `{link}`.", quote=True)

# -------------------- START COMMAND (PRIVATE) --------------------
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    add_user(user_id, message.from_user.first_name, message.from_user.username)

    if is_banned(user_id):
        return await message.reply_text("🚫 **You are banned from using this bot.**", quote=True)

    if not await check_fsub(client, user_id):
        return await message.reply_text(
            f"👋 **Hello {message.from_user.first_name}!**\n\n"
            "⚠️ **You must join our channel to use this bot.**\n"
            "Click below, then press **I've Joined**.",
            reply_markup=await force_sub_button(),
            quote=True
        )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD TO GROUP", url=f"http://t.me/{app.me.username}?startgroup=true")],
        [InlineKeyboardButton("ℹ️ HELP", callback_data="help"),
         InlineKeyboardButton("📊 STATS", callback_data="stats")]
    ])
    await message.reply_text(
        f"✨ **Welcome {message.from_user.first_name}!**\n\n"
        f"🚀 **Aavya Bypass Bot** is online.\n"
        f"📂 **Service:** Link Bypasser (supports most shortlinks)\n\n"
        f"Send me any short link and I'll give you the direct link.",
        reply_markup=buttons,
        quote=True
    )

# -------------------- HELP COMMAND (PRIVATE) --------------------
@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    if is_banned(message.from_user.id):
        return await message.reply_text("🚫 Banned.", quote=True)
    if not await check_fsub(client, message.from_user.id):
        return await message.reply_text(
            "⚠️ **Join our channel first!**",
            reply_markup=await force_sub_button(),
            quote=True
        )
    await message.reply_text(
        "🔍 **How to use me**\n\n"
        "1. Send me any shortlink (e.g., `exe.io`, `shortingly.com`)\n"
        "2. I will process it and give you the direct link.\n"
        "3. Add me to your group – I will work there too.\n\n"
        "**Commands:**\n"
        "/start - Main menu\n"
        "/help - This message",
        quote=True
    )

# -------------------- BYPASS LOGIC (PRIVATE) --------------------
@app.on_message(filters.text & ~filters.command(["start", "help", "stats", "users", "groups", "broadcast", "ban", "unban", "leave", "setfsub", "setlink"]) & filters.private)
async def handle_bypass_private(client, message):
    user_id = message.from_user.id
    if is_banned(user_id):
        return await message.reply_text("🚫 **You are banned.**", quote=True)

    user_link = message.text.strip()
    if "http" not in user_link:
        return

    if not await check_fsub(client, user_id):
        return await message.reply_text(
            "⚠️ **Access Denied!**\nPlease join our channel first.",
            reply_markup=await force_sub_button(),
            quote=True
        )

    await process_bypass(client, message, user_link)

# -------------------- GROUP HANDLER --------------------
@app.on_message(filters.text & filters.group)
async def handle_bypass_group(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    add_group(chat_id, message.chat.title)

    if is_banned(user_id):
        return await message.reply_text("🚫 **You are banned from using this bot.**", quote=True)

    user_link = message.text.strip()
    if "http" not in user_link:
        return

    if not await check_fsub(client, user_id):
        return await message.reply_text(
            f"👤 **{message.from_user.first_name}**, you must join our channel to use this bot in groups.\n"
            f"Click below, join, then try again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 JOIN CHANNEL", url=FORCE_SUB_LINK)]]),
            quote=True
        )

    await process_bypass(client, message, user_link)

# -------------------- COMMON BYPASS FUNCTION --------------------
async def process_bypass(client, message, user_link):
    start_time = time.time()
    try:
        await client.send_reaction(message.chat.id, message.id, "👀")
    except:
        pass

    msg = await message.reply_text("🔍 **Processing your link...**", quote=True)

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        res = requests.get(api_url, timeout=30).json()

        if res.get("status"):
            bypassed = res["info"]["bypass"]
            original = res["info"]["original"]
            time_taken = time.time() - start_time

            response_text = (
                f"✅ **Successfully Bypassed!**\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔗 **Original Link:**\n{original}\n\n"
                f"🚀 **Bypassed Link:**\n{bypassed}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏱️ **Time:** `{time_taken:.2f}s`\n"
                f"👤 **User:** @{message.from_user.username or 'User'}\n"
                f"🤖 **Bot:** @{app.me.username}\n"
                f"👩‍💻 **Dev:** @AAVYAXBOTS"
            )
            try:
                await client.send_reaction(message.chat.id, message.id, "🔥")
            except:
                pass
            await msg.edit(response_text, disable_web_page_preview=False)
        else:
            await msg.edit("❌ **Bypass Failed!**\nReason: Link not supported or API error.")
    except requests.exceptions.Timeout:
        await msg.edit("⏰ **Timeout error** – API took too long to respond.")
    except Exception as e:
        await msg.edit(f"❌ **Error:** `{str(e)[:100]}`")

# -------------------- RUN BOT --------------------
if __name__ == "__main__":
    from threading import Thread
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: server.run(host="0.0.0.0", port=port)).start()
    print("🚀 Bot is starting...")
    app.run()
