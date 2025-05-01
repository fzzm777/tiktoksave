
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests
import os
import re

API_TOKEN = "7540767411:AAESj0--99f-O6H542u_l3t1qpNzL-Szh4U"
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

def download_tiktok_ssstik(url):
    try:
        session = requests.Session()
        headers = {
            "origin": "https://ssstik.io",
            "referer": "https://ssstik.io/en",
            "user-agent": "Mozilla/5.0"
        }
        data = {"id": url, "locale": "en", "tt": "ok"}
        r = session.post("https://ssstik.io/abc?url=dl", headers=headers, data=data)
        video_url = re.search(r'href="(https://[^"]+)"', r.text)
        if video_url:
            video_resp = session.get(video_url.group(1))
            if video_resp.status_code == 200 and video_resp.headers.get("content-type", "").startswith("video"):
                filename = "video.mp4"
                with open(filename, "wb") as f:
                    f.write(video_resp.content)
                return filename
        return None
    except Exception:
        return None

def download_video(url):
    try:
        url = requests.head(url, allow_redirects=True).url
        if "tiktok.com" in url:
            return download_tiktok_ssstik(url)
    except:
        return None
    return None

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

@dp.message_handler(lambda msg: 'tiktok.com' in msg.text)
async def handle_video(message: types.Message):
    lang = get_lang(message.from_user.id)
    await message.reply(messages[lang]['downloading'])
    video_path = download_video(message.text)
    if video_path and os.path.getsize(video_path) > 0:
        await message.reply_video(open(video_path, 'rb'))
        os.remove(video_path)
    else:
        await message.reply(messages[lang]['error'])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
