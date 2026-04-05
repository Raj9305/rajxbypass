import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
# MongoDB URL (Render/Koyeb variables mein daalna)
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0)) # Apna ID daalo

BYPASS_API_KEY = "SH4DAW-D4DY" 
FORCE_SUB_LINK = "https://t.me/+T-IiOXWR6dFiZDA9"
FSUB_ID = os.environ.get("FSUB_ID", "") 

# --- DATABASE SETUP ---
db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']

server = Flask(__name__)

@server.route('/')
def status():
    return 'Bot is Online with MongoDB & Admin Features!'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- HELPER FUNCTIONS ---
def add_user(user_id):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id})

async def check_join(client, message):
    if not FSUB_ID: return True
    try:
        await client.get_chat_member(FSUB_ID, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply_text(
            f"**HELLO @{message.from_user.username} !!**\n\n"
            "**YOU MUST JOIN OUR GROUP TO USE THIS BOT!**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📢 JOIN OUR GROUP 📢", url=FORCE_SUB_LINK)
            ]])
        )
        return False
    except Exception:
        return True

# --- ADMIN COMMANDS ---
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats(client, message):
    count = users_col.count_documents({})
    await message.reply_text(f"**📊 TOTAL USERS IN DATABASE: {count}**")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID) & filters.reply)
async def broadcast(client, message):
    msg = message.reply_to_message
    users = users_col.find({})
    done = 0
    failed = 0
    for user in users:
        try:
            await msg.copy(chat_id=user['user_id'])
            done += 1
        except:
            failed += 1
    await message.reply_text(f"**📢 BROADCAST DONE!**\n\n**✅ SUCCESS: {done}**\n**❌ FAILED: {failed}**")

# --- USER COMMANDS ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    add_user(message.from_user.id)
    if not await check_join(client, message): return
    
    welcome_text = (
        f"**👋 HELLO @{message.from_user.username} !!**\n\n"
        f"**WELCOME TO PRO BYPASS BOT !**\n\n"
        f"**MAINTAINED BY: @aavyaxbots ✅**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🚀 **I AM A SUPER FAST LINK BYPASS BOT.**\n"
        f"✨ **JUST SEND ANY SHORT LINK AND WATCH THE MAGIC!**\n\n"
        f"📢 **STAY JOINED IN THE CHANNEL FOR UPDATES.**"
    )

    await message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕𝗔𝗗𝗗 𝗜𝗡 𝗚𝗥𝗢𝗨𝗣➕", url=f"http://t.me/{app.me.username}?startgroup=true")],
            [InlineKeyboardButton("𝗕𝗨𝗬 𝗔𝗣𝗜🚀", url="https://t.me/cyb3rB4nn3r")]
        ])
    )

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if not user_link.startswith("http"): return

    add_user(message.from_user.id)
    if not await check_join(client, message): return

    start_time = time.time()
    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("**BYPASSING... ⏳**")

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        res = requests.get(api_url, timeout=30)
        data = res.json()

        if data.get("status") == True and "info" in data:
            bypassed = data["info"]["bypass"]
            original = data["info"]["original"]
            time_taken = time.time() - start_time
            
            response_text = (
                f"**🚀𝗔𝗔𝗩𝗬𝗔 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧🚀**\n\n"
                f"🙋‍♂️ **REQUESTED BY: @{message.from_user.username}**\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"🔗 **𝗢𝗥𝗜𝗚𝗜𝗡𝗔𝗟:**\n> {original}\n\n"
                f"🚀 **𝗕𝗬𝗣𝗔𝗦𝗦𝗘𝗗 :**\n> {bypassed}\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⏱️ **TIME TAKEN: `{time_taken:.2f}S`**\n"
                f"👩‍💻 **𝗗𝗘𝗩: @aavyaxbots ✅**"
            )
            
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            
            await msg.edit(
                response_text,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕𝗔𝗗𝗗 𝗜𝗡 𝗚𝗥𝗢𝗨𝗣➕", url=f"http://t.me/{app.me.username}?startgroup=true")],
                    [InlineKeyboardButton("𝗕𝗨𝗬 𝗔𝗣𝗜", url="https://t.me/cyb3rB4nn3r")]
                ])
            )
        else:
            await msg.edit(f"**API ERROR: `{data.get('msg', 'INVALID LINK')}` ❌**")
            
    except Exception as e:
        await msg.edit(f"**SYSTEM ERROR: `{str(e)}` ❌**")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
