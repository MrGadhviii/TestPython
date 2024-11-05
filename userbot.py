import os
import random
import asyncio
import logging
from telethon import TelegramClient, events, functions, types

# Set up logging to show only warnings and errors (to reduce noise)
logging.basicConfig(level=logging.WARNING)

# Replace with your actual credentials
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'
OWNER_ID = 7029363479  # Replace with your user ID

session_file = 'my_session'
client = TelegramClient(session_file, API_ID, API_HASH)

original_name = None
original_profile_photo = None

# Track online status and suppress timeout messages
is_owner_online = True
timeout_interval = 60  # Set a reasonable interval to check online status

async def main():
    global original_name, original_profile_photo, is_owner_online

    await client.start()

    # Get and store the original name and profile photo
    me = await client.get_me()
    original_name = me.first_name
    photos = await client.get_profile_photos('me')
    if photos:
        original_profile_photo = photos[0]

    print("Bot is running...")

    # Auto-reply when offline
    @client.on(events.NewMessage(incoming=True))
    async def handle_incoming_message(event):
        global is_owner_online
        sender = await event.get_sender()

        # Only respond with an offline message if the owner is offline and it's a private message
        if event.is_private and sender.id != OWNER_ID:
            if not is_owner_online:
                print(f"Owner is offline. Sending offline message to {sender.id}.")
                offline_message = await event.reply(
                    f"<b>Owner is currently offline</b>. He will reply as soon as possible.", 
                    parse_mode='html'
                )
                await asyncio.sleep(10)
                await client.delete_messages(event.chat_id, offline_message.id)

    # Monitor the owner's status
    @client.on(events.UserUpdate(OWNER_ID))
    async def check_owner_status(event):
        global is_owner_online
        user_status = event.status

        # Check if the owner is online or offline
        if isinstance(user_status, (types.UserStatusOnline, types.UserStatusEmpty)):
            if not is_owner_online:  # If changing from offline to online
                is_owner_online = True
                print("Owner is now online.")
                await client.send_message(OWNER_ID, "Bot detected you are online.")
        else:
            if is_owner_online:  # If changing from online to offline
                is_owner_online = False
                print("Owner is now offline.")

    # Scheduled task to check status if updates are missed
    async def monitor_owner_status():
        while True:
            try:
                status = await client.get_entity(OWNER_ID)
                if isinstance(status.status, (types.UserStatusOnline, types.UserStatusEmpty)):
                    if not is_owner_online:
                        is_owner_online = True
                        print("Owner is now online (checked via scheduled task).")
                else:
                    if is_owner_online:
                        is_owner_online = False
                        print("Owner is now offline (checked via scheduled task).")
            except Exception as e:
                print(f"Error checking owner status: {e}")
            await asyncio.sleep(timeout_interval)

    # Start the monitoring coroutine in the background
    client.loop.create_task(monitor_owner_status())

    # Run the client until disconnected
    await client.run_until_disconnected()

asyncio.run(main())
