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


@bot.callback_query_handler(func=lambda call: call.data == "auth")
def callback_login(call: telebot.types.CallbackQuery):
    bot.send_message(call.message.chat.id, "Введите логин")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, login_entered)


def login_entered(message):
    potential_login = message.text
    bot.send_message(message.from_user.id, "Введите пароль")
    bot.register_next_step_handler(message, password_entered, potential_login)


def password_entered(message, login):
    potential_password = message.text
    bot.send_message(message.from_user.id, f"{login} | {potential_password}")
