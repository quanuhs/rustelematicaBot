import telebot
from .models import BotSettings

settings = BotSettings.objects.filter().first()

if settings is not None:
    bot = telebot.TeleBot(settings.token)
else:
    bot = telebot.TeleBot(None)


def handle_message(request):
    # global bot
    #
    # new_settings = BotSettings.objects.filter().first()
    #
    # if new_settings is not None:
    #     bot = telebot.TeleBot(settings.token)

    bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])


@bot.message_handler(content_types=['text'])
def directives(message: telebot.types.Message):
    bot.send_message(message.from_user.id, "cool")
