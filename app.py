import os
import requests
from flask import Flask
from pyrogram import Client, filters

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
# FIXED KEY: SH4DAW-D4DY (A ke saath)
BYPASS_API_KEY = "SH4DAW-D4DY" 

server = Flask(__name__)

@server.route('/')
def status():
    return 'Bot is Online!'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("**Aavya Bypass Bot V6!**\n\nLink bhejo, ab bypass pakka chalega. 🚀")

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if not user_link.startswith("http"): return

    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("Bypassing... ⚡")

    try:
        # Correct API Link with SH4DAW key
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        res = requests.get(api_url, headers=headers, timeout=20)
        data = res.json()

        # Logic for success
        if data.get("status") == True or "bypassed_url" in data:
            final_link = data.get("bypassed_url") or data.get("link")
            
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            
            await msg.edit(f"**Success!** ✅\n\n`{final_link}`")
        else:
            # API error dikhao agar key ya link galat ho
            error_msg = data.get("msg") or data.get("message") or "Unknown API Error"
            await msg.edit(f"**API Issue:** `{error_msg}` ❌")
            
    except Exception as e:
        await msg.edit(f"**System Error:** `{str(e)}` ❌")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
