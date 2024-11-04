import asyncio
from telethon import TelegramClient, events

# Replace with your bot's actual API ID, API Hash, and Bot Token
API_ID = 24808705
API_HASH = 'adf3a113ab32bb2792338477f156dc86'
BOT_TOKEN = '8015052876:AAEi65xgC7XzKRcn9hKGBY48wDlFrUDQuUY'

# Create the Telegram client using the bot token
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Handles the /start command from the user."""
    await event.reply("Welcome! Please enter your phone number (this is just a test, not real login).")

    @client.on(events.NewMessage(incoming=True, from_users=event.sender_id))
    async def phone_step(event):
        phone_number = event.raw_text.strip()
        await event.reply(f"Received phone number {phone_number}. Now pretend sending OTP...")
        
        # Simulate OTP prompt
        await event.reply("Enter the OTP (this is simulated; real bots don’t use OTPs).")

        @client.on(events.NewMessage(incoming=True, from_users=event.sender_id))
        async def otp_step(event):
            otp = event.raw_text.strip()
            await event.reply(f"Received OTP: {otp}. Simulation complete. You are now 'logged in'.")

async def main():
    print("Bot is running...")
    await client.start()
    await client.run_until_disconnected()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
