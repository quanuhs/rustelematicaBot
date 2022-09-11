import telebot
from .models import BotSettings


class TelegramBot(telebot.TeleBot):
    def set_token(self, new_token):
        self.token = new_token


bot: TelegramBot = TelegramBot(None)


def handle_message(request):
    settings = BotSettings.objects.filter().first()

    if settings is not None:
        bot.set_token(settings.token)
    else:
        return

    bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])


@bot.message_handler(content_types=['text'])
def directives(message: telebot.types.Message):
    bot.send_message(message.from_user.id, "cool")
