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

# Command list with descriptions
commands = {
    '.hello': 'Greet the user.',
    '.send random': 'Send 10 random greetings.',
    '.clone': 'Clone the first name and profile picture of the user.',
    '.back': 'Revert to the original name and profile picture.',
    '.purge <number>': 'Delete the specified number of messages from the chat.',
    '.block': 'Block the user from whom the message was received.',
    '.weather': 'Get the current weather information (placeholder).',
    '.love': 'Send a random love message and a Hindi shayari.',
    '.cmd': 'List all available commands and their descriptions.'
}

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

        # Handle .cmd command
        if event.raw_text.strip() == '.cmd':
            command_list = "\n".join([f"{cmd}: {desc}" for cmd, desc in commands.items()])
            await client.send_message(event.chat_id, f"Available Commands:\n{command_list}")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .hello command
        elif event.raw_text.strip() == '.hello':
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
            await client(functions.contacts.BlockRequest(recipient.id))
            await client.send_message(event.chat_id, "User has been blocked.")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .weather command
        elif event.raw_text.strip() == '.weather':
            # You will need to replace with a valid API call to get weather
            # For example purposes, let's just return a static message
            weather_info = "It's sunny with a temperature of 25°C."  # Placeholder
            await client.send_message(event.chat_id, weather_info)
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

        # Handle .love command
        elif event.raw_text.strip() == '.love':
            love_messages = [
                "You are my sunshine, my only sunshine.",
                "I love you to the moon and back.",
                "Every moment spent with you is like a beautiful dream.",
                "You have my heart, and I am forever yours."
            ]
            shayari = [
                "तेरा मेरा रिश्ता कुछ ऐसा है, जैसे कि खुदा का इशारा कुछ ऐसा है।",
                "तेरे बिना अधूरी है ज़िंदगी मेरी, जैसे बारिश बिना नीर की।",
                "तू ही है मेरा चाँद, तू ही है मेरी तन्हाई, तेरे बिना मेरा कोई नसीब नहीं।"
            ]
            random_love_message = random.choice(love_messages)
            random_shayari = random.choice(shayari)
            await client.send_message(event.chat_id, f"{random_love_message}\n\nShayari:\n{random_shayari}")
            await client.delete_messages(event.chat_id, event.id)  # Delete command immediately

    await client.run_until_disconnected()

asyncio.run(main())
