import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from cloudipsp import Api, Checkout

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a bot instance
bot = Bot(token="1413286061:AAH2McHA3Oy4r_Qbr-Ol_-efz0WmLwW4rtY")

# Create a Dispatcher instance
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Set up the Cloudipsp API client
api = Api(merchant_id="1526526", secret_key="rj6IEGhpd3tJsfMZhbCqtU8hNo5KIo8Z")

# Command handler for /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Welcome to Fondy UA Bot!")

# Command handler for /payment
@dp.message_handler(commands=["payment"])
async def payment(message: types.Message):
    checkout = Checkout(api=api)
    data = {
        "amount": 5,  # The payment amount in hryvnas
        "currency": "UAH",
        "order_desc": "Payment for Fondy UA Bot",
        "response_url": "https://t.me/DistancionkaDermoBot",  # URL to receive payment response
    }
    response = checkout.url(data)
    payment_url = response['checkout_url']
    await message.reply(f"Please make a payment of 5 hryvnas using this link: {payment_url}")



# Run the bot
if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
