import os
import requests
from flask import Flask
from pyrogram import Client, filters

# --- CONFIG (Koyeb/Render ke Environment Variables se aayenge) ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BYPASS_API_KEY = "SH4DOW-D4DY"

server = Flask(__name__)

@server.route('/')
def status():
    return 'Bot is Running!'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("**Link Bypass Bot V4!**\n\nLink bhejo, bypass ho jayega. ⚡")

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if not user_link.startswith("http"): return

    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("Bypassing... ⏳")

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        # Adding Browser-like Headers
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(api_url, headers=headers, timeout=15)
        
        data = res.json()
        final_link = data.get("bypassed_url") or data.get("link")

        if final_link:
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            await msg.edit(f"**Success!** ✅\n\n`{final_link}`")
        else:
            await msg.edit(f"**API Response:** `{data}`")
            
    except Exception as e:
        await msg.edit(f"**Error:** `{str(e)}` ❌")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
