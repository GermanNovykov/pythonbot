import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from fondy import API




# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a bot instance
bot = Bot(token="1413286061:AAH2McHA3Oy4r_Qbr-Ol_-efz0WmLwW4rtY")

# Create a Dispatcher instance
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

api = API(merchant_id="1526526", merchant_key="rj6IEGhpd3tJsfMZhbCqtU8hNo5KIo8Z", server_callback_url="https://t.me/DistancionkaDermoBot")
class paycheck(StatesGroup):
    check = State()


# Command handler for /start
@dp.message_handler(commands=['start'])
async def start_checkout(message: types.Message):
    # Retrieve the necessary parameters from the user
    order_id = '10'
    amount = 5 * 100
    order_desc = 'Pay for bot'
    response_url = 'https://t.me/DistancionkaDermoBot'
    currency = 'UAH'

    # Call the checkout method to get the checkout URL
    result = api.checkout(order_id, amount, order_desc, response_url, currency)
    print(result)
    # Get the checkout URL from the result
    checkout_url = result['response']['checkout_url']

    # Send the checkout URL to the user
    await message.reply(checkout_url)

@dp.message_handler(commands=['check'])
async def start_checkout(message: types.Message):
    result = api.order_status('10')
    print(result)

# Run the bot
if __name__ == "__main__":
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)