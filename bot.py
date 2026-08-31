import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = '8739969583:AAElf56svjZmlHbj-ZfaSaasHS_7qZQcTmU'
API_URL = 'https://cryptomfo.rf.gd/api/bot_client.php'
API_SECRET = 'your_client_secret_key_here_change_me'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def api_request(action: str, chat_id: int = 0, data: dict = None):
    url = API_URL
    headers = {
        'X-Bot-Secret': API_SECRET,
        'Content-Type': 'application/json'
    }
    payload = {'action': action, 'chat_id': chat_id}
    if data:
        payload.update(data)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            return await response.json()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    chat_id = message.chat.id
    
    result = await api_request('check_binding', chat_id)
    
    if result.get('success'):
        user = result['user']
        await message.answer(
            f"✅ *Telegram успешно привязан!*\n\n"
            f"👤 Аккаунт: {user['email']}\n"
            f"💰 Баланс: ${user['balance']:.2f}",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            "👋 Добро пожаловать в Crypto MFO!\n\n"
            "🔑 Введите код, который вы получили на сайте для привязки Telegram аккаунта.\n\n"
            "📋 Код состоит из 6 цифр и действует 5 минут."
        )

@dp.message()
async def handle_code(message: types.Message):
    chat_id = message.chat.id
    code = message.text.strip()
    
    if not code.isdigit() or len(code) != 6:
        await message.answer(
            "❌ Код должен состоять из 6 цифр.\n"
            "Пожалуйста, введите код правильно."
        )
        return
    
    result = await api_request('verify_code', chat_id, {'code': code})
    
    if result.get('success'):
        await message.answer(
            f"✅ {result['message']}\n\n"
            f"Теперь вы можете войти на сайт без пароля!"
        )
    else:
        await message.answer(
            f"❌ {result.get('message', 'Ошибка')}\n\n"
            "Проверьте код и попробуйте еще раз."
        )

async def main():
    print("🚀 Бот клиентов запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())