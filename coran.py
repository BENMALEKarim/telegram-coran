import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to get the audio URL based on the surah number
def get_surah_audio_url(surah_number):
    if 1 <= surah_number <= 114:
        formatted_number = f"{surah_number:03}"
        url = f"https://server8.mp3quran.net/afs/{formatted_number}.mp3"
        return url
    else:
        return None

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("مرحبًا! من فضلك أدخل رقم السورة (001 إلى 114) للحصول على التسجيل الصوتي.")

# Handler for receiving surah number input
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        surah_number = int(update.message.text)
        audio_url = get_surah_audio_url(surah_number)

        if audio_url:
            # Send the audio file (Quran recitation)
            await context.bot.send_audio(chat_id=update.message.chat.id, audio=audio_url)
        else:
            await update.message.reply_text("عذرًا، لم أتمكن من العثور على تلك السورة. يرجى إدخال رقم بين 001 و 114.")
    except ValueError:
        await update.message.reply_text("يرجى إدخال رقم صالح.")


# Main function to run the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your bot's token from BotFather
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    
    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add the command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()

