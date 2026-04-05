import os
import requests
from flask import Flask
from pyrogram import Client, filters

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BYPASS_API_KEY = "SH4DAW-D4DY" 

server = Flask(__name__)

@server.route('/')
def status():
    return 'Bot is Online!'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("**Aavya Bypass Bot V7!**\n\nAb link output pakka dikhega. 🔥")

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if not user_link.startswith("http"): return

    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("Bypassing... ⚡")

    try:
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(api_url, headers=headers, timeout=20)
        data = res.json()

        # Saari keys check kar rahe hain taaki 'None' na aaye
        final_link = (
            data.get("bypassed_url") or 
            data.get("link") or 
            data.get("url") or 
            data.get("short_url")
        )

        if final_link:
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            
            await msg.edit(f"**Success!** ✅\n\n`{final_link}`")
        else:
            # Agar bypass nahi hua toh poora response dikhao debug ke liye
            await msg.edit(f"**API Response:**\n`{data}`")
            
    except Exception as e:
        await msg.edit(f"**System Error:** `{str(e)}` ❌")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
