import os
import asyncio
import sys
from telethon import TelegramClient, events

# Replace with your actual API ID and API Hash
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'
PHONE_NUMBER = '+918780836084'  # Your temporary phone number

# Get the OTP from command line arguments
OTP = sys.argv[1] if len(sys.argv) > 1 else None

# Session name for storing login session
session_file = 'owner_session'

# Delete the session file if it exists (optional)
if os.path.exists(f'{session_file}.session'):
    os.remove(f'{session_file}.session')

# Create the Telegram client
client = TelegramClient(session_file, API_ID, API_HASH)

# Variable to track if the owner is online
is_online = False

async def main():
    global is_online
    await client.start(phone=PHONE_NUMBER, password=OTP)  # Use OTP for login
    print("Logged in successfully.")

    # ... (rest of your code remains unchanged)

# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
