# pip install python-telegram-bot

import logging
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from telegram import InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from open_ai_chat import OpenAIChat
from text_to_speach import TextToSpeech
from utils import download_file


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

config = None

ai_agent = None
tts = None

async def start(update, context):
    await update.message.reply_text("Hello! Welcome to Amin's telegram bot")
    logger.info(f"User {update.message.from_user.id} started the bot")


async def help(update, context):
    await update.message.reply_text(
        """
    /start -> Welcome message
    /help
    /clear -> Clear chat history
    """
    )
    logger.info(f"User {update.message.from_user.id} requested help")


async def clear_chat(update, context):
    if not await is_allowed(update):
        await update.message.reply_text("not allowed...")
        return
    if ai_agent:
        await ai_agent.clear(update.message.from_user.id)
        await update.message.reply_text("Chat history cleared")

    logger.info(f"User {update.message.from_user.id} cleared chat history")


async def is_allowed(update):
    result = str(update.message.from_user.id) in config["allowed_users"]
    if not result:
        logger.info(f"User {update.message.from_user.id} is not allowed")
    return result


async def handle_message(update, context):
    logger.info(f"User {update.message.from_user.id} sent a message")
    if not await is_allowed(update):
        await update.message.reply_text("not allowed...")
        return

    text = update.message.text

    reply_text = "Simple text response..."
    if text == "id":
        reply_text = str(update.message.from_user.id)
    elif text == "password":
        reply_text = "?"
    elif text == config["password"]:
        id = str(update.message.from_user.id)
        if id not in config["allowed_users"]:
            config["allowed_users"].append(id)
    elif text == "list users":
        if await is_allowed(update):
            reply_text = "\n".join(config["allowed_users"])
    elif ai_agent:
            reply_text = await ai_agent.generate(text, user_id=update.message.from_user.id)

    await update.message.reply_text(reply_text)


async def voice_handler(update, context):
    if not await is_allowed(update):
        await update.message.reply_text("not allowed...")
        return
    if ai_agent is None:
        await update.message.reply_text("AI agent not available")
        return
    logger.info(f"User {update.message.from_user.id} sent a voice message")

    voice = update.message.voice
    file = await context.bot.getFile(voice.file_id)
    ogg_filename = os.path.join('tmp', f'{voice.file_id}.oga')
    mp3_filename = ogg_filename.replace('.oga', '.mp3')
    
    logger.info(f"Downloading voice message to {ogg_filename}")
    await download_file(file.file_path, ogg_filename)

    audio = AudioSegment.from_ogg(ogg_filename)
    audio.export(mp3_filename, format="mp3")
    text = await ai_agent.transcript(mp3_filename)
    os.remove(ogg_filename)
    os.remove(mp3_filename)
    await update.message.reply_text(text)

    reply_text = await ai_agent.generate(text, user_id=update.message.from_user.id)
    await update.message.reply_text(reply_text)

    await tts.generate(reply_text, file_name=mp3_filename)
    with open(mp3_filename, 'rb') as mp3_file:
        await context.bot.send_voice(chat_id=update.message.chat_id, voice=InputFile(mp3_file, filename="response.mp3"))
    os.remove(mp3_filename)


if __name__ == "__main__":
    load_dotenv()
    config = {
        "token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "password": os.getenv("TELEGRAM_BOT_PASSWORD"),
        "allowed_users": os.getenv("TELEGRAM_BOT_ALLOWED_USERS").split(","),
    }

    ai_agent = OpenAIChat()
    tts = TextToSpeech()
    app = Application.builder().token(config["token"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("clear", clear_chat))

    # app.add_handler(CommandHandler("restart_system", restart_system))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))

    app.run_polling(poll_interval=2)
