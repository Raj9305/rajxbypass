import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait
from pymongo import MongoClient

# --- 𝗖𝗢𝗡𝗙𝗜𝗚 (𝗥𝗘𝗡𝗗𝗘𝗥 𝗩𝗔𝗥𝗜𝗔𝗕𝗟𝗘𝗦) ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URL = os.environ.get("MONGO_URL", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0)) 

BYPASS_API_KEY = os.environ.get("BYPASS_API_KEY", "SH4DAW-D4DY")
FORCE_SUB_LINK = os.environ.get("FORCE_SUB_LINK", "https://t.me/+T-IiOXWR6dFiZDA9")
FSUB_ID = os.environ.get("FSUB_ID", "") 

# --- 𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘 ---
db_client = MongoClient(MONGO_URL)
db = db_client['BypassBotDB']
users_col = db['users']
chats_col = db['chats']

server = Flask(__name__)
@server.route('/')
def status(): return '𝗨𝗟𝗧𝗥𝗔 𝗦𝗘𝗖𝗨𝗥𝗘 𝗕𝗢𝗧 𝗢𝗡𝗟𝗜𝗡𝗘'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- 𝗨𝗧𝗜𝗟𝗦 ---
def add_serve(chat_id, is_group=False):
    col = chats_col if is_group else users_col
    key = "chat_id" if is_group else "user_id"
    if not col.find_one({key: chat_id}):
        col.insert_one({key: chat_id})

async def is_subscribed(client, message):
    if not FSUB_ID: return True
    try:
        await client.get_chat_member(FSUB_ID, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply_text(
            f"⚠️ **𝗛𝗘𝗟𝗟𝗢 @{message.from_user.username} !!**\n\n"
            f"**𝗬𝗢𝗨 𝗠𝗨𝗦𝗧 𝗝𝗢𝗜𝗡 𝗢𝗨𝗥 𝗚𝗥𝗢𝗨𝗣 𝗧𝗢 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗕𝗢𝗧!**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("➕ **𝗝𝗢𝗜𝗡 𝗢𝗨𝗥 𝗚𝗥𝗢𝗨𝗣** ➕", url=FORCE_SUB_LINK)
            ]])
        )
        return False
    except: return True

# --- 𝗔𝗨𝗧𝗢 𝗦𝗔𝗩𝗘 𝗖𝗛𝗔𝗧𝗦 ---
@app.on_message(filters.new_chat_members)
async def auto_save_group(client, message):
    if any(m.id == (await client.get_me()).id for m in message.new_chat_members):
        add_serve(message.chat.id, is_group=True)

# --- 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 ---
@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats(client, message):
    u_count = users_col.count_documents({})
    c_count = chats_col.count_documents({})
    await message.reply_text(f"📊 **𝗦𝗧𝗔𝗧𝗦:**\n\n👤 **𝗨𝗦𝗘𝗥𝗦: {u_count}**\n👥 **𝗚𝗥𝗢𝗨𝗣𝗦: {c_count}**")

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID) & filters.reply)
async def broadcast(client, message):
    msg = message.reply_to_message
    status = await message.reply_text("🚀 **𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗦𝗧𝗔𝗥𝗧𝗘𝗗...**")
    done = 0
    # Broadcast to Users & Groups
    for collection, key in [(users_col, 'user_id'), (chats_col, 'chat_id')]:
        for entry in collection.find({}):
            try:
                await msg.copy(chat_id=entry[key])
                done += 1
            except FloodWait as e:
                time.sleep(e.value)
                await msg.copy(chat_id=entry[key])
                done += 1
            except: pass
    await status.edit(f"📢 **𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗗𝗢𝗡𝗘! 𝗧𝗢𝗧𝗔𝗟 𝗥𝗘𝗖𝗜𝗣𝗜𝗘𝗡𝗧𝗦: {done}**")

# --- 𝗠𝗔𝗜𝗡 𝗟𝗢𝗚𝗜𝗖 (𝗢𝗪𝗡𝗘𝗥 𝗢𝗡𝗟𝗬) ---
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("❌ **𝗦𝗢𝗥𝗥𝗬! 𝗢𝗡𝗟𝗬 𝗧𝗛𝗘 𝗢𝗪𝗡𝗘𝗥 𝗖𝗔𝗡 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗕𝗢𝗧.**")
    
    add_serve(message.from_user.id)
    if not await is_subscribed(client, message): return
    
    await message.reply_text(
        f"👋 **𝗛𝗘𝗟𝗟𝗢 @{message.from_user.username} !!**\n\n"
        f"**𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗢𝗪𝗡𝗘𝗥! 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧 𝗜𝗦 𝗥𝗘𝗔𝗗𝗬.**\n\n"
        f"**𝗝𝗨𝗦𝗧 𝗦𝗘𝗡𝗗 𝗧𝗛𝗘 𝗟𝗜𝗡𝗞 𝗕𝗘𝗟𝗢𝗪!**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ **𝗔𝗗𝗗 𝗠𝗘 𝗧𝗢 𝗚𝗥𝗢𝗨𝗣** ➕", url=f"http://t.me/{app.me.username}?startgroup=true")],
            [InlineKeyboardButton("💰 **𝗣𝗔𝗜𝗗 𝗔𝗣𝗜** 💰", url="https://t.me/cyb3rB4nn3r")]
        ])
    )

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("❌ **𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!**")

    user_link = message.text.strip()
    if not user_link.startswith("http"): return
    if not await is_subscribed(client, message): return

    start_time = time.time()
    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("**𝗕𝗬𝗣𝗔𝗦𝗦𝗜𝗡𝗚... ⏳**")

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        res = requests.get(api_url, timeout=30).json()

        if res.get("status"):
            bypassed = res["info"]["bypass"]
            original = res["info"]["original"]
            time_taken = time.time() - start_time
            
            response_text = (
                f"⚡ **𝗔𝗔𝗩𝗬𝗔 𝗕𝗬𝗣𝗔𝗦𝗦 𝗕𝗢𝗧** ⚡\n\n"
                f"🙋‍♂️ **𝗥𝗘𝗤𝗨𝗘𝗦𝗧𝗘𝗗 𝗕𝗬: @{message.from_user.username}**\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"🔗 **𝗢𝗥𝗜𝗚𝗜𝗡𝗔𝗟:**\n> {original}\n\n"
                f"🚀 **𝗕𝗬𝗣𝗔𝗦𝗦𝗘𝗗:**\n> {bypassed}\n\n"
                f"━━━━━━━━━━━━━━━\n"
                f"⏱️ **𝗧𝗜𝗠𝗘 𝗧𝗔𝗞𝗘𝗡: `{time_taken:.2f}𝗦`**\n"
                f"👩‍💻 **𝗠𝗔𝗜𝗡𝗧𝗔𝗜𝗡𝗘𝗗 𝗕𝗬: @aavyaxbots ✅**"
            )
            
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            
            await msg.edit(response_text, disable_web_page_preview=True)
        else:
            await msg.edit(f"❌ **𝗔𝗣𝗜 𝗘𝗥𝗥𝗢𝗥: `{res.get('msg', '𝗙𝗔𝗜𝗟𝗘𝗗')}`**")
            
    except Exception as e:
        await msg.edit(f"❌ **𝗘𝗥𝗥𝗢𝗥: `{str(e)}`**")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
