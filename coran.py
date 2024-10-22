import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionnaire des récitateurs et leurs URLs correspondantes
RECITERS = {
    1: ("أحمد العجمي", "https://server10.mp3quran.net/ajm/"),
    2: ("عبد الرحمن السديس", "https://server11.mp3quran.net/sds/"),
    3: ("مشاري العفاسي", "https://server8.mp3quran.net/afs/"),
    4: ("عبد الباسط عبد الصمد", "https://server7.mp3quran.net/basit/"),
    5: ("ماهر المعيقلي", "https://server12.mp3quran.net/maher/"),
    6: ("ياسر الدوسري", "https://server11.mp3quran.net/yasser/"),
    7: ("سعود الشريم", "https://server7.mp3quran.net/shur/"),
    8: ("سعد الغامدي", "https://server7.mp3quran.net/s_gmd/"),
}

# Liste des sourates avec leurs numéros et noms en arabe
SURAH_LIST = [
    "1. الفاتحة", "2. البقرة", "3. آل عمران", "4. النساء", "5. المائدة", "6. الأنعام", "7. الأعراف", "8. الأنفال",
    "9. التوبة", "10. يونس", "11. هود", "12. يوسف", "13. الرعد", "14. إبراهيم", "15. الحجر", "16. النحل",
    "17. الإسراء", "18. الكهف", "19. مريم", "20. طه", "21. الأنبياء", "22. الحج", "23. المؤمنون", "24. النور",
    "25. الفرقان", "26. الشعراء", "27. النمل", "28. القصص", "29. العنكبوت", "30. الروم", "31. لقمان", "32. السجدة",
    "33. الأحزاب", "34. سبأ", "35. فاطر", "36. يس", "37. الصافات", "38. ص", "39. الزمر", "40. غافر",
    "41. فصلت", "42. الشورى", "43. الزخرف", "44. الدخان", "45. الجاثية", "46. الأحقاف", "47. محمد", "48. الفتح",
    "49. الحجرات", "50. ق", "51. الذاريات", "52. الطور", "53. النجم", "54. القمر", "55. الرحمن", "56. الواقعة",
    "57. الحديد", "58. المجادلة", "59. الحشر", "60. الممتحنة", "61. الصف", "62. الجمعة", "63. المنافقون", "64. التغابن",
    "65. الطلاق", "66. التحريم", "67. الملك", "68. القلم", "69. الحاقة", "70. المعارج", "71. نوح", "72. الجن",
    "73. المزمل", "74. المدثر", "75. القيامة", "76. الإنسان", "77. المرسلات", "78. النبأ", "79. النازعات", "80. عبس",
    "81. التكوير", "82. الإنفطار", "83. المطففين", "84. الإنشقاق", "85. البروج", "86. الطارق", "87. الأعلى", "88. الغاشية",
    "89. الفجر", "90. البلد", "91. الشمس", "92. الليل", "93. الضحى", "94. الشرح", "95. التين", "96. العلق",
    "97. القدر", "98. البينة", "99. الزلزلة", "100. العاديات", "101. القارعة", "102. التكاثر", "103. العصر", "104. الهمزة",
    "105. الفيل", "106. قريش", "107. الماعون", "108. الكوثر", "109. الكافرون", "110. النصر", "111. المسد", "112. الإخلاص",
    "113. الفلق", "114. الناس"
]

# Variable globale pour stocker l'état du bot
user_reciter_choice = {}

# Fonction pour obtenir l'URL de l'audio en fonction du réciteur et du numéro de la sourate
def get_surah_audio_url(surah_number, reciter_url):
    if 1 <= surah_number <= 114:
        formatted_number = f"{surah_number:03}"
        url = f"{reciter_url}{formatted_number}.mp3"
        return url
    else:
        return None

# Commande /start qui demande à l'utilisateur de choisir un réciteur
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user_reciter_choice[chat_id] = {"reciter": None, "surah": None}  # Initialiser l'état pour cet utilisateur
    
    reciters_message = "اختر القارئ:\n"
    for num, (reciter_name, _) in RECITERS.items():
        reciters_message += f"{num}. {reciter_name}\n"

    await update.message.reply_text(reciters_message + "أدخل رقم القارئ (1-8):")

# Handler pour recevoir le choix du réciteur
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user_choice = update.message.text

    try:
        user_choice = int(user_choice)
        
        if user_reciter_choice[chat_id]["reciter"] is None:
            # L'utilisateur choisit un réciteur
            if user_choice in RECITERS:
                reciter_name, reciter_url = RECITERS[user_choice]
                user_reciter_choice[chat_id]["reciter"] = reciter_url  # Sauvegarder le choix du réciteur
                surah_message = "اختر السورة:\n" + "\n".join(SURAH_LIST)
                await update.message.reply_text(f"لقد اخترت {reciter_name}.\n{surah_message}\nالآن أدخل رقم السورة (1-114):")
            else:
                await update.message.reply_text("عذرًا، هذا الرقم غير صالح. أدخل رقمًا بين 1 و 8.")
        else:
            # L'utilisateur choisit une sourate
            if 1 <= user_choice <= 114:
                reciter_url = user_reciter_choice[chat_id]["reciter"]
                audio_url = get_surah_audio_url(user_choice, reciter_url)

                if audio_url:
                    await context.bot.send_audio(chat_id=chat_id, audio=audio_url)
                else:
                    await update.message.reply_text("عذرًا، لم أتمكن من العثور على السورة.")
            else:
                await update.message.reply_text("عذرًا، أدخل رقم سورة بين 1 و 114.")

    except ValueError:
        await update.message.reply_text("يرجى إدخال رقم صالح.")

# Main function to run the bot
def main():
    # Remplacer 'YOUR_BOT_TOKEN' par le token de ton bot fourni par BotFather
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    
    # Créer l'application
    application = Application.builder().token(TOKEN).build()

    # Ajouter les gestionnaires de commandes et de messages
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Démarrer le bot
    application.run_polling()

if __name__ == '__main__':
    main()
