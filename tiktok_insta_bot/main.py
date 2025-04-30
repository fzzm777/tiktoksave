
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests
import os

API_TOKEN = os.getenv("7540767411:AAESj0--99f-O6H542u_l3t1qpNzL-Szh4U")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_languages = {}

messages = {
    'en': {
        'start': "👋 Send me a TikTok or Instagram link and I will download the video without watermark!",
        'downloading': "⏳ Downloading...",
        'error': "❌ Failed to download video. Please check the link.",
        'choose_lang': "🌐 Choose your language:",
        'set_lang': "✅ Language set to English.",
    },
    'ru': {
        'start': "👋 Пришли мне ссылку на TikTok или Instagram, и я скачаю видео без водяных знаков!",
        'downloading': "⏳ Загружаю...",
        'error': "❌ Не удалось скачать видео. Проверь ссылку.",
        'choose_lang': "🌐 Выберите язык:",
        'set_lang': "✅ Язык установлен на русский.",
    }
}

lang_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
lang_keyboard.add(KeyboardButton("🇬🇧 English"), KeyboardButton("🇷🇺 Русский"))

def get_lang(user_id):
    return user_languages.get(user_id, 'en')

def download_video(url):
    if "tiktok.com" in url:
        api_url = f"https://api.tikmate.app/api/lookup?url={url}"
        resp = requests.get(api_url).json()
        if 'token' in resp:
            video_url = f"https://tikmate.app/download/{resp['token']}/{resp['id']}.mp4"
            filename = "video.mp4"
    elif "instagram.com" in url:
        api_url = f"https://saveig.app/api/ajaxSearch"
        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        data = {"q": url, "t": "media", "lang": "en"}
        resp = requests.post(api_url, headers=headers, data=data).json()
        try:
            video_url = resp["links"][0]["url"]
            filename = "video.mp4"
        except:
            return None
    else:
        return None
    video = requests.get(video_url)
    with open(filename, "wb") as f:
        f.write(video.content)
    return filename

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    lang = get_lang(message.from_user.id)
    await message.reply(messages[lang]['start'])

@dp.message_handler(commands=['language'])
async def language_cmd(message: types.Message):
    lang = get_lang(message.from_user.id)
    await message.reply(messages[lang]['choose_lang'], reply_markup=lang_keyboard)

@dp.message_handler(lambda msg: msg.text in ["🇬🇧 English", "🇷🇺 Русский"])
async def set_language(message: types.Message):
    if message.text == "🇬🇧 English":
        user_languages[message.from_user.id] = 'en'
        await message.reply(messages['en']['set_lang'], reply_markup=ReplyKeyboardRemove())
    else:
        user_languages[message.from_user.id] = 'ru'
        await message.reply(messages['ru']['set_lang'], reply_markup=ReplyKeyboardRemove())

@dp.message_handler(lambda msg: 'tiktok.com' in msg.text or 'instagram.com' in msg.text)
async def handle_video(message: types.Message):
    lang = get_lang(message.from_user.id)
    await message.reply(messages[lang]['downloading'])
    video_path = download_video(message.text)
    if video_path:
        await message.reply_video(open(video_path, 'rb'))
        os.remove(video_path)
    else:
        await message.reply(messages[lang]['error'])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
