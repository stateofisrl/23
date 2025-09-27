import re
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.tl.types import KeyboardButtonUrl

# --- Telegram API credentials ---
API_ID = 24878661
API_HASH = "7fd279b83c40a0d4228b89978685638a"

# --- Use session string instead of file ---
SESSION_STRING = "wQQddWAvd90uN+mfpX1+1/hPW5PZQWMtCl67G+kBd+yOqXdzVd9DAeulJLtfP8aHf52g39e5h5Y+7djtitP4rw=="

# --- Channel IDs ---
SOURCE_CHANNEL = "@Signals_Pumps_Free"
TARGET_CHANNEL = "@aixauusdbtcusd_trade"

# --- Replacement Settings ---
REPLACE_WITH = "@aimanagementteambot"

# --- Flask keep-alive server ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()


# --- Utility functions ---
def clean_text(text):
    """Replace any @mention or http/https link with REPLACE_WITH."""
    if not text:
        return text
    text = re.sub(r"@\w+", REPLACE_WITH, text, flags=re.IGNORECASE)
    text = re.sub(r"https?://[^\s)>\]]+", REPLACE_WITH, text, flags=re.IGNORECASE)
    return text

def get_custom_button():
    """Create a custom button like @ControllerBot."""
    return [KeyboardButtonUrl(text="💬 Join Our Bot", url="https://t.me/aimanagementteambot")]

def replace_button_links(reply_markup):
    """Replace links in buttons and add a custom button row."""
    custom_button = get_custom_button()
    if not reply_markup:
        return None
    try:
        new_rows = []
        for row in reply_markup.rows:
            new_buttons = []
            for button in row.buttons:
                if hasattr(button, 'url') and button.url:
                    new_url = re.sub(r"https?://[^\s)>\]]+", REPLACE_WITH, button.url, flags=re.IGNORECASE)
                    new_buttons.append(KeyboardButtonUrl(text=button.text, url=new_url))
                else:
                    new_buttons.append(button)
            new_rows.append(type(row)(buttons=new_buttons))
        # Add custom button as a new row
        new_rows.append(type(new_rows[0])(buttons=custom_button))
        return type(reply_markup)(rows=new_rows)
    except Exception as e:
        print(f"⚠️ Error replacing button links: {e}")
        return reply_markup


# --- Bot logic ---
async def run_bot():
    # Use session string here
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def handler(event):
        try:
            message = event.message
            print(f"📥 New message received: {message.id}")  # Debug line
            reply_markup = replace_button_links(message.reply_markup) if message.reply_markup else None
            text_content = clean_text(message.text or message.message or message.raw_text)

            if message.media:
                await client.send_file(TARGET_CHANNEL, message.media, caption=text_content or "", buttons=reply_markup)
            elif text_content:
                await client.send_message(TARGET_CHANNEL, text_content, buttons=reply_markup)
            elif reply_markup:
                await client.send_message(TARGET_CHANNEL, "📢", buttons=reply_markup)

            print(f"✅ Forwarded new message ID {message.id}")
        except Exception as e:
            print(f"⚠️ Error forwarding message {event.id}: {e}")

    await client.start()
    print("🚀 Bot is running 24/7 and will forward NEW messages only...")
    await client.run_until_disconnected()


# --- Start keep-alive server and bot ---
keep_alive()

while True:
    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"💥 Bot crashed with error: {e}. Restarting in 10s...")
        asyncio.sleep(10)
