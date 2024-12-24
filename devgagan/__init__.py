import asyncio
import logging
from pyromod import listen
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB
from telethon.sync import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.get_event_loop()
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

app = Client(
    "RestrictBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=10
)

pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
telethon_client = TelegramClient('telethon_repo', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

async def auto_ping():
    while True:
        try:
            getme = await app.get_me()
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Error in auto_ping: {e}")
            await asyncio.sleep(10)

tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]

async def create_ttl_index():
    try:
        await token.create_index("expires_at", expireAfterSeconds=0)
        logging.info("MongoDB TTL index created.")
    except Exception as e:
        logging.error(f"Error creating TTL index: {e}")

async def setup_database():
    await create_ttl_index()

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await setup_database()
    await app.start()
    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name
    
    if STRING:
        try:
            await pro.start()
        except Exception as e:
            logging.error(f"Failed to start client with STRING: {e}")
    
    asyncio.create_task(auto_ping())

if __name__ == "__main__":
    loop.run_until_complete(restrict_bot())
