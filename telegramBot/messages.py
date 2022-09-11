import telebot
from models import BotSettings

token = BotSettings.objects.filter().first().token
bot = telebot.TeleBot(token)


def handle_message(request):
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])


@bot.message_handler(content_types=['text'])
def directives(message: telebot.types.Message):
    bot.send_message(message.from_user.id, "cool")
