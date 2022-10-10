from time import sleep
from celery import shared_task
from .models import BotSettings

from telebot import TeleBot


@shared_task(name="notify_after_test")
def notify_after_test(telegram_id, message, markup_keyboard):
    """Переодическое задание. Уведомляет пользователя через 4 минуты с момента включения режима тестирования)"""
    
    
    bot_settings = BotSettings.objects.filter().first()
    if bot_settings is None:
        return False
    
    bot = TeleBot(bot_settings.token)
    bot.send_message(telegram_id, message, reply_markup=markup_keyboard)

    
    return True



    