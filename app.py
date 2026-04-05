import os
import requests
from flask import Flask
from pyrogram import Client, filters

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID", "YOUR_API_ID")) # Render/Koyeb variables se lega
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
BYPASS_API_KEY = "SH4DOW-D4DY" 

server = Flask(__name__)

@server.route('/')
def status():
    return 'Bot is Online!'

app = Client("BypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("**Aavya Bypass Bot V5!**\n\nLink bhejo, ab pakka bypass hoga. 🔥")

@app.on_message(filters.text & filters.private)
async def handle_bypass(client, message):
    user_link = message.text.strip()
    if not user_link.startswith("http"):
        return

    # 1. Processing Reaction (Eyes 👀)
    try: await client.send_reaction(message.chat.id, message.id, "👀")
    except: pass

    msg = await message.reply_text("Bypassing... ⏳")

    try:
        # Final API URL with your Key
        api_url = f"https://link-btpass.vercel.app/search?key={BYPASS_API_KEY}&link={user_link}"
        
        # Adding headers to look like a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        res = requests.get(api_url, headers=headers, timeout=20)
        data = res.json()

        # Check API status or success
        if data.get("status") == True or data.get("status") == "success" or data.get("bypassed_url"):
            final_link = data.get("bypassed_url") or data.get("link")
            
            # 2. Success Reaction (Fire 🔥)
            try: await client.send_reaction(message.chat.id, message.id, "🔥")
            except: pass
            
            await msg.edit(f"**Success!** ✅\n\n`{final_link}`")
        else:
            # Display API message if key/link is invalid
            api_msg = data.get("msg") or data.get("message") or "Invalid API Key/Response"
            await msg.edit(f"**API Error:** `{api_msg}` ❌")
            
    except Exception as e:
        await msg.edit(f"**System Error:** `{str(e)}` ❌")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: server.run(host="0.0.0.0", port=8080)).start()
    app.run()
