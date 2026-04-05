import os
import requests
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BYPASS_API_KEY = "SH4DAW-D4DY" 
FORCE_SUB_LINK = "https://t.me/+T-IiOXWR6dFiZDA9"
# Note: Force sub ke liye invite link ki jagah channel ID ya username (-100xxx) lagta hai.
FSUB_ID = os.environ.get("FSUB_ID", "") 

server = Flask(__name__)

@server.route('/')
def status():
    return 'Bot is Running with Force Join!'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Fancy text format function
def get_fancy_text(original, bypassed, time_taken, user_fname):
    return (
        f"**⚡ AAVYA BYPASS BOT ⚡**\n\n"
        f"🙋‍♂️ **Requested by:** {user_fname}\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"🔗 **Original:**\n`{original}`\n\n"
        f"🚀 **Bypassed:**\n`{bypassed}`\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏱️ **Time Taken:** `{time_taken:.2f}s`\n"
        f"👩‍💻 **Dev:** @aavyaxbots ✅"
    )

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"**Welcome {message.from_user.first_name}!**\n\n"
        "Main ek fast Link Bypass bot hoon. Bas link bhejo aur magic dekho! ✨",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me To Group", url=f"http://t.me/{app.me.username}?startgroup=true")],
            [InlineKeyboardButton("📢 Updates Channel", url=FORCE_SUB_LINK)]
        ])
    )

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    # Sirf Links detect karega
    user_link = message.text.strip()
    if not user_link.startswith("http"):
        return

    # --- FORCE JOIN CHECK ---
    if FSUB_ID:
        try:
            await client.get_chat_member(FSUB_ID, message.from_user.id)
        except UserNotParticipant:
            return await message.reply_text(
                "**❌ Access Denied!**\n\nBot use karne ke liye aapko hamare channel ko join karna hoga.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Join Channel 📢", url=FORCE_SUB_LINK)
                ]])
            )
        except Exception:
            pass

    # Timer aur Reaction
    start_time = time.time()
    user_fname = message.from_user.first_name

    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("Bypassing... ⏳")

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        res = requests.get(api_url, timeout=30)
        data = res.json()

        if data.get("status") == True and "info" in data:
            final_link = data["info"]["bypass"]
            original_link = data["info"]["original"]
            time_taken = time.time() - start_time
            
            fancy_text = get_fancy_text(original_link, final_link, time_taken, user_fname)
            
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            
            await msg.edit(
                fancy_text,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Me To Group", url=f"http://t.me/{app.me.username}?startgroup=true")],
                    [InlineKeyboardButton("Dev ✅", url="https://t.me/aavyaxbots")]
                ])
            )
        else:
            await msg.edit(f"**API Issue:** `{data.get('msg', 'Error')}` ❌")
            
    except Exception as e:
        await msg.edit(f"**Error:** `{str(e)}` ❌")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
