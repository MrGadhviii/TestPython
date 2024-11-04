import os
import asyncio
from telethon import TelegramClient, events

# Replace with your actual API ID and API Hash
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'

# Session name for storing login session
session_file = 'owner_session'

# Create the Telegram client
client = TelegramClient(session_file, API_ID, API_HASH)

# Variable to track if the owner is online
is_online = False

async def main():
    global is_online
    
    # Prompt the owner for their phone number
    PHONE_NUMBER = input("Enter your phone number: ")

    # Start the client with the phone number
    await client.start(phone=PHONE_NUMBER)

    # Wait for the client to be logged in
    await client.connect()
    if not await client.is_user_authorized():
        # If not authorized, ask for the OTP
        OTP = input("Please enter the OTP sent to your Telegram app: ")
        await client.sign_in(phone=PHONE_NUMBER, code=OTP)

    print("Logged in successfully.")

    # Access the owner's profile
    me = await client.get_me()
    print("Owner's Profile:", me.stringify())

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

    print("Bot is running and listening for messages...")
    await client.run_until_disconnected()  # Run the main function

# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
