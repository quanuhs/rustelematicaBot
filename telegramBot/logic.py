import telebot
from telebot import types
from .api_handler import RustelematicaAPI

from .models import BotDictionary


class TelegramBot(telebot.TeleBot):
    def set_token(self, new_token):
        self.token = new_token


bot: TelegramBot = TelegramBot(None)
api: RustelematicaAPI = RustelematicaAPI(None)


class Markups:
    def __init__(self, language):
        self.language = language

    @property
    def text(self):
        return BotDictionary.objects.filter(language=self.language).first()

    def start_menu(self):
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row(self.text.menu_btn_status, self.text.menu_btn_check)
        keyboard.row('Logout')
        return keyboard

    def auth(self):
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text=self.text.menu_btn_login, callback_data="auth")
        keyboard.add(button)
        return keyboard


def handle_message(request, settings):
    bot.set_token(settings.token)
    api.set_api(settings.api_key)

    bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])


@bot.message_handler(commands=['start'])
def start(message):
    _markup = Markups("RU")
    text_description = _markup.text.welcome_text
    bot.send_message(message.from_user.id, text_description, reply_markup=_markup.auth())


@bot.callback_query_handler(func=lambda call: True)
def callback_login(call):
    bot.send_message(call.message.chat.id, "okey")
    # msg = bot.message_handler(call.message.chat.id, "Введите логин")
    # bot.register_next_step_handler(msg, login_entered)


def login_entered(message):
    bot.send_message(message.from_user.id, message.text)
