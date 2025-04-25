# Pok
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatPermissions
from datetime import datetime, timedelta
import threading
import time
import json
import os

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='media_cleaner_bot.log'
)
logger = logging.getLogger(__name__)

# توکن ربات شما
TOKEN = "7986275489:AAEQW06TDtf81fkzO8INz4s_avlmRCtwFHk"

# فایل ذخیره تنظیمات
SETTINGS_FILE = "bot_settings.json"

# زمان پیش‌فرض برای پاک کردن (دقیقه)
DEFAULT_DELAY = 7

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

bot_settings = load_settings()

def delete_media_after_delay(chat_id, message_id, delay_minutes=DEFAULT_DELAY):
    time.sleep(delay_minutes * 60)
    try:
        if str(chat_id) in bot_settings and bot_settings[str(chat_id)]['active']:
            updater.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"پیام {message_id} در چت {chat_id} پاک شد.")
    except Exception as e:
        logger.error(f"خطا در پاک کردن پیام {message_id}: {e}")

def handle_media(update, context):
    message = update.message
    chat_id = message.chat_id
    
    if str(chat_id) not in bot_settings or bot_settings[str(chat_id)]['active']:
        if (message.photo or message.video or message.animation or message.sticker):
            message_id = message.message_id
            
            thread = threading.Thread(
                target=delete_media_after_delay,
                args=(chat_id, message_id)
            )
            thread.start()
            
            logger.info(f"رسانه جدید در چت {chat_id} ثبت شد و بعد از {DEFAULT_DELAY} دقیقه پاک می‌شود.")

def start(update, context):
    update.message.reply_text(
        "🤖 ربات پاک‌کننده رسانه‌ها فعال است!\n\n"
        "🔧 دستورات مدیریتی:\n"
        "/روشن - فعال کردن ربات در این گروه\n"
        "/خاموش - غیرفعال کردن ربات در این گروه\n"
        "/وضعیت - نمایش وضعیت فعلی ربات\n\n"
        "⚠️ توجه: ربات باید به عنوان ادمین با مجوز 'حذف پیام‌ها' اضافه شود."
    )

def turn_on(update, context):
    chat_id = update.message.chat_id
    if str(chat_id) not in bot_settings:
        bot_settings[str(chat_id)] = {'active': True}
    else:
        bot_settings[str(chat_id)]['active'] = True
    
    save_settings(bot_settings)
    update.message.reply_text("✅ ربات در این گروه فعال شد.\nرسانه‌ها (عکس، فیلم، گیف، استیکر) بعد از 7 دقیقه به طور خودکار پاک می‌شوند.")

def turn_off(update, context):
    chat_id = update.message.chat_id
    if str(chat_id) not in bot_settings:
        bot_settings[str(chat_id)] = {'active': False}
    else:
        bot_settings[str(chat_id)]['active'] = False
    
    save_settings(bot_settings)
    update.message.reply_text("❌ ربات در این گروه غیرفعال شد.\nرسانه‌ها پاک نخواهند شد.")

def status(update, context):
    chat_id = update.message.chat_id
    if str(chat_id) in bot_settings and bot_settings[str(chat_id)]['active']:
        update.message.reply_text("🟢 وضعیت: فعال\nرسانه‌ها بعد از 7 دقیقه پاک می‌شوند.")
    else:
        update.message.reply_text("🔴 وضعیت: غیرفعال\nرسانه‌ها پاک نمی‌شوند.")

def error_handler(update, context):
    logger.error(f"خطا در پردازش پیام: {context.error}")

def main():
    global updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # افزودن هندلرهای دستورات
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("روشن", turn_on))
    dp.add_handler(CommandHandler("خاموش", turn_off))
    dp.add_handler(CommandHandler("وضعیت", status))

    # افزودن هندلر برای رسانه‌ها
    dp.add_handler(MessageHandler(
        Filters.photo | Filters.video | Filters.animation | Filters.sticker,
        handle_media
    ))

    # افزودن هندلر خطا
    dp.add_error_handler(error_handler)

    updater.start_polling()
    logger.info("ربات شروع به کار کرد...")
    updater.idle()

if __name__ == '__main__':
    main()
