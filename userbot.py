import os
import random
import asyncio
import requests
from telethon import TelegramClient, events, functions, types

# Replace with your actual credentials
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'
OWNER_ID = 7029363479  # Replace with your user ID

session_file = 'my_session'
client = TelegramClient(session_file, API_ID, API_HASH)

original_name = None
original_profile_photo = None  # Store original profile photo info

# Global variable to track online status
is_owner_online = True

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
        
        # Get the owner's name
        owner = await client.get_me()
        owner_name = owner.first_name  # Use owner's first name

        # Check if the message is private and not from the owner
        if event.is_private and sender.id != OWNER_ID:
            if not is_owner_online:
                offline_message = await event.reply(
                    f"<b>{owner_name} is Offline,</b> He will reply as soon as 💯.", 
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
                # Notify users that the owner is now online
                await client.send_message(OWNER_ID, "Owner is now online. Ask me anything!")
        else:
            if is_owner_online:  # If changing from online to offline
                is_owner_online = False

    # Outgoing message commands
    @client.on(events.NewMessage(outgoing=True))
    async def handle_outgoing_message(event):
        global original_name, original_profile_photo

        # Handle .hello command
        if event.raw_text.strip() == '.hello':
            recipient = await event.get_chat()
            username = recipient.first_name if recipient.first_name else "User"
            response_message = await client.send_message(recipient.id, f"Hello {username}, how are you?")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .send random command
        elif event.raw_text.strip() == '.send random':
            messages = ["Hello!", "How's it going?", "Good day!", "Hey!", "Hi there!"]
            random_messages = [random.choice(messages) for _ in range(10)]
            sent_messages = []
            for msg in random_messages:
                message = await client.send_message(event.chat_id, msg)
                sent_messages.append(message)
            await asyncio.sleep(30)
            await client.delete_messages(event.chat_id, [msg.id for msg in sent_messages])
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .clone command
        elif event.raw_text.strip() == '.clone':
            recipient = await event.get_chat()
            recipient_name = recipient.first_name
            recipient_photos = await client.get_profile_photos(recipient.id)

            # Clone the name
            await client(functions.account.UpdateProfileRequest(first_name=recipient_name))

            # Clone the profile picture if available
            if recipient_photos:
                photo = recipient_photos[0]
                # Download the photo
                await client.download_media(photo, file='cloned_profile_pic.jpg')
                await client(functions.photos.UploadProfilePhotoRequest(file='cloned_profile_pic.jpg'))

            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .back command
        elif event.raw_text.strip() == '.back':
            if original_name:
                await client(functions.account.UpdateProfileRequest(first_name=original_name))
            if original_profile_photo:
                await client(functions.photos.UploadProfilePhotoRequest(original_profile_photo))
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .purge command
        elif event.raw_text.startswith('.purge '):
            try:
                count = int(event.raw_text.split(' ')[1])
                async for message in client.iter_messages(event.chat_id, limit=count):
                    await client.delete_messages(event.chat_id, message.id)
                await client.send_message(event.chat_id, f"Deleted {count} messages.")
            except ValueError:
                await client.send_message(event.chat_id, "Please specify a valid number of messages to delete.")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .block command
        elif event.raw_text.strip() == '.block':
            recipient = await event.get_chat()
            await client(BlockRequest(recipient.id))
            await client.send_message(event.chat_id, f"Blocked {recipient.first_name}.")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .love command
        elif event.raw_text.strip() == '.love':
            # Fetch random shayari from the web
            try:
                response = requests.get('https://shayari-api.herokuapp.com/api/v1/shayari')
                if response.status_code == 200:
                    shayari_data = response.json()
                    random_shayari = shayari_data['shayari']
                else:
                    random_shayari = "Could not fetch shayari at this time."
            except Exception as e:
                random_shayari = "Error fetching shayari: " + str(e)

            await client.send_message(event.chat_id, f"Here’s a lovely shayari:\n{random_shayari}")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .cmd command to list all commands
        elif event.raw_text.strip() == '.cmd':
            command_list = (
                ".hello - Greet the user.\n"
                ".send random - Send random messages.\n"
                ".clone - Clone the recipient's name and profile picture.\n"
                ".back - Revert to the original name and profile picture.\n"
                ".purge {n} - Delete the last n messages.\n"
                ".block - Block the user.\n"
                ".love - Send a random love shayari.\n"
                ".cmd - List all commands."
            )
            await client.send_message(event.chat_id, f"Available commands:\n{command_list}")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

    await client.run_until_disconnected()

asyncio.run(main())
    
