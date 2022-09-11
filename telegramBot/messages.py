import telebot
from .models import BotSettings


bot:telebot.TeleBot = telebot.TeleBot(None, threaded=False)


def handle_message(request):
    global bot

    settings = BotSettings.objects.filter().first()

    if settings is not None:
        bot = telebot.TeleBot(settings.token)
    else:
        return

    bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])


@bot.message_handler(content_types=['text'])
def directives(message: telebot.types.Message):
    bot.send_message(message.from_user.id, "cool")
