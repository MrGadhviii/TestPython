import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# Replace with your actual API ID, API Hash, and Bot Token
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'
BOT_TOKEN = '8015052876:AAEi65xgC7XzKRcn9hKGBY48wDlFrUDQuUY'  # Your actual bot token

# Session name for storing login session
session_file = 'owner_session'

# Create the Telegram client for the user
client = TelegramClient(session_file, API_ID, API_HASH)

# Store user state
user_state = {}

async def send_message(event, message):
    await event.reply(message)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await send_message(event, "Please enter your phone number:")
    user_state[event.sender_id] = {'step': 'phone_number'}

@client.on(events.NewMessage(incoming=True))
async def handle_incoming_message(event):
    sender_id = event.sender_id
    state = user_state.get(sender_id)

    if state is None:
        return  # Ignore messages from users who haven't started the process

    if state['step'] == 'phone_number':
        phone_number = event.raw_text.strip()
        user_state[sender_id]['phone_number'] = phone_number
        await send_message(event, "OTP sent. Please enter the OTP you received:")

        try:
            await client.start(phone=phone_number)
            await client.send_code_request(phone_number)
            user_state[sender_id]['step'] = 'otp'
        except Exception as e:
            await send_message(event, f"Error: {e}")
            return

    elif state['step'] == 'otp':
        otp = event.raw_text.strip()
        try:
            await client.sign_in(state['phone_number'], otp)
            user_state[sender_id]['step'] = 'logged_in'
            await send_message(event, "Logged in successfully.")
            # Now continue with your bot functionality
            await client.run_until_disconnected()
        except SessionPasswordNeededError:
            await send_message(event, "Two-step verification is enabled. Please enter your password:")
            user_state[sender_id]['step'] = 'password'
        except Exception as e:
            await send_message(event, f"Error during login: {e}")

    elif state['step'] == 'password':
        password = event.raw_text.strip()
        try:
            await client.sign_in(password=password)
            user_state[sender_id]['step'] = 'logged_in'
            await send_message(event, "Logged in successfully.")
            # Now continue with your bot functionality
            await client.run_until_disconnected()
        except Exception as e:
            await send_message(event, f"Error during password entry: {e}")

# Start the bot
async def main():
    # Start the bot using the bot token
    await client.start(bot_token=BOT_TOKEN)
    print("Bot is running...")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
