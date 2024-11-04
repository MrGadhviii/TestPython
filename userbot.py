import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# Replace with actual API credentials
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'
BOT_TOKEN = '8015052876:AAEi65xgC7XzKRcn9hKGBY48wDlFrUDQuUY'

# Session file for storing the real account login
owner_session = 'owner_session'

# Initialize bot client
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
owner_client = TelegramClient(owner_session, API_ID, API_HASH)

# Variables to track status
is_online = False
login_state = False  # Tracks if login process is ongoing

async def login_owner(event):
    """ Starts login for the owner's real account using phone number and OTP. """
    await event.reply("Please enter your phone number:")
    
    @bot.on(events.NewMessage(incoming=True, from_users=event.sender_id))
    async def handle_phone(event):
        phone = event.raw_text.strip()
        
        try:
            # Start login with phone number
            await owner_client.connect()
            if not await owner_client.is_user_authorized():
                await owner_client.send_code_request(phone)
                await event.reply("OTP sent to your Telegram app. Please enter the OTP:")
                
                @bot.on(events.NewMessage(incoming=True, from_users=event.sender_id))
                async def handle_otp(event):
                    otp = event.raw_text.strip()
                    
                    try:
                        # Complete login with OTP
                        await owner_client.sign_in(phone, otp)
                        await event.reply("Logged in successfully.")
                    except PhoneCodeInvalidError:
                        await event.reply("Invalid OTP. Please try again.")
        except SessionPasswordNeededError:
            await event.reply("Two-step verification is enabled. Please enter your password:")
            
            @bot.on(events.NewMessage(incoming=True, from_users=event.sender_id))
            async def handle_password(event):
                password = event.raw_text.strip()
                await owner_client.sign_in(password=password)
                await event.reply("Logged in with password successfully.")

@bot.on(events.NewMessage)
async def handle_bot_message(event):
    """ Main event handler for bot messages, including commands and auto-reply. """
    global is_online
    
    if event.raw_text == '/start':
        await login_owner(event)
    elif event.raw_text.strip() == '.hello':
        recipient = await event.get_chat()
        username = recipient.first_name if recipient.first_name else "User"
        
        # Send personalized message
        await bot.send_message(recipient.id, f"Hello {username}, how are you?")
        await bot.delete_messages(event.chat_id, event.id)
    elif event.is_private:
        # Auto-reply if owner is offline
        if not is_online:
            offline_msg = await event.reply("Owner is offline. See you soon!")
            await asyncio.sleep(10)
            await bot.delete_messages(event.chat_id, offline_msg.id)

@owner_client.on(events.NewMessage(outgoing=True))
async def handle_outgoing_message(event):
    """ Set online status when owner sends a message. """
    global is_online
    is_online = True
    await asyncio.sleep(2)  # Adjust timing if needed
    is_online = False

async def main():
    print("Bot is running. Waiting for messages...")
    await bot.run_until_disconnected()

# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
    
