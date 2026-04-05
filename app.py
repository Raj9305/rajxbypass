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
FORCE_SUB_LINK = "https://t.me/+4hW0nmW34rRjN2Fl"

# --- DATABASE ---
db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']
chats_col = db['chats']

server = Flask(__name__)
@server.route('/')
def status(): return 'BOT IS RUNNING'

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

# --- START COMMAND ---
@app.on_message(filters.command("start"))
async def start(client, message):
    add_serve(message.chat.id, is_group=(message.chat.type != "private"))
    is_joined = await check_fsub(client, message)
    
    buttons = []
    if not is_joined:
        buttons.append([InlineKeyboardButton("✅𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟✅", url=FORCE_SUB_LINK)])
    
    buttons.append([InlineKeyboardButton("🎀𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗚𝗥𝗢𝗨𝗣🎀", url=f"http://t.me/{app.me.username}?startgroup=true")])

    text = (
        f"👋 **𝗛𝗘𝗟𝗟𝗢 @{message.from_user.username or 'User'} !!**\n\n"
        f"**𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗔𝗔𝗩𝗬𝗔 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧 !**\n\n"
        f"🚀 **𝗜 𝗔𝗠 𝗔 𝗦𝗨𝗣𝗘𝗥 𝗙𝗔𝗦𝗧 𝗟𝗜𝗡𝗞 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧.**\n"
        f"✨ **𝗝𝗨𝗦𝗧 𝗦𝗘𝗡𝗗 𝗔𝗡𝗬 𝗦𝗛𝗢𝗥𝗧 𝗟𝗜𝗡𝗞 𝗔𝗡𝗗 𝗪𝗔𝗧𝗖𝗛 𝗧𝗛𝗘 𝗠𝗔𝗚𝗜𝗖!**"
    )
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- BYPASS LOGIC ---
@app.on_message(filters.text & ~filters.command(["start", "stats", "broadcast"]))
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if "http" not in user_link: return

    add_serve(message.chat.id, is_group=(message.chat.type != "private"))

    if not await check_fsub(client, message):
        return await message.reply_text(
            "⚠️ **𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!**\n\n**𝗕𝗬𝗣𝗔𝗦𝗦 𝗞𝗘 𝗟𝗜𝗬𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟 𝗝𝗢𝗜𝗡 𝗞𝗔𝗥𝗡𝗔 𝗭𝗔𝗥𝗢𝗢𝗥𝗜 𝗛𝗔𝗜.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url=FORCE_SUB_LINK)]]),
            quote=True
        )

    start_time = time.time()
    try: await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="👀")
    except: pass

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
                f"🔗 **𝗢𝗥𝗜𝗚𝗜𝗡𝗔𝗟:**\n`{original}`\n\n"
                f"🚀 **𝗕𝗬𝗣𝗔𝗦𝗦𝗘𝗗:**\n`{bypassed}`\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⏱️ **𝗧𝗜𝗠𝗘: `{time_taken:.2f}𝗦`**\n"
                f"👩‍💻 **𝗗𝗘𝗩: @AAVYAXBOTS ✅**"
            )
            try: await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="🔥")
            except: pass
            await msg.edit(response_text, disable_web_page_preview=True)
        else:
            await msg.edit("❌ **𝗔𝗣𝗜 𝗘𝗥𝗥𝗢𝗥! 𝗟𝗜𝗡𝗞 𝗡𝗢𝗧 𝗦𝗨𝗣𝗣𝗢𝗥𝗧𝗘𝗗.**")
    except:
        await msg.edit("❌ **𝗦𝗘𝗥𝗩𝗘𝗥 𝗘𝗥𝗥𝗢𝗥!**")

# --- ADMIN COMMANDS ---
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats(client, message):
    u_count = users_col.count_documents({})
    c_count = chats_col.count_documents({})
    await message.reply_text(f"📊 **𝗦𝗧𝗔𝗧𝗦:**\n\n👤 **𝗨𝗦𝗘𝗥𝗦: {u_count}**\n👥 **𝗖𝗛𝗔𝗧𝗦: {c_count}**")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID) & filters.reply)
async def broadcast(client, message):
    msg = message.reply_to_message
    await message.reply_text("🚀 **𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗦𝗧𝗔𝗥𝗧𝗘𝗗...**")
    for collection, key in [(users_col, 'user_id'), (chats_col, 'chat_id')]:
        for entry in collection.find({}):
            try: await msg.copy(chat_id=entry[key])
            except FloodWait as e: time.sleep(e.value); await msg.copy(chat_id=entry[key])
            except: pass
    await message.reply_text("📢 **𝗗𝗢𝗡𝗘!**")

if __name__ == "__main__":
    from threading import Thread
    port = int(os.environ.get("PORT", 8080))
    Thread(target=lambda: server.run(host="0.0.0.0", port=port)).start()
    app.run()
