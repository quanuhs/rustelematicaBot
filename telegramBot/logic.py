import telebot
from telebot import types
from .api_handler import RustelematicaAPI

from .models import BotDictionary, UserInfo


class TelegramBot(telebot.TeleBot):
    def set_token(self, new_token):
        self.token = new_token


class TemporaryBase(dict):

    def add_user(self, user_id):
        self.update({user_id: {"status": self.LOGIN(), "id": user_id}})

    @staticmethod
    def PASSWORD_1():
        return "password_1"

    @staticmethod
    def PASSWORD_2():
        return "password_2"

    @staticmethod
    def LOGIN():
        return "login"


bot: TelegramBot = TelegramBot(None)
api: RustelematicaAPI = RustelematicaAPI(None)

temp_base = TemporaryBase()


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
    UserInfo.objects.create(telegram_id=call.from_user.id, name=call.message.from_user.username or "unknown")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if temp_handle_text(message):
        return

    if user_handle_text(message):
        return

    start()


def check_login(potential_login):
    return True


def check_password_1(login, potential_password_1):
    return True


def check_password_2(login, password_1, potential_password_2):
    return True


def create_user(temp_user):
    pass


def temp_handle_text(message):
    temp_user: UserInfo = UserInfo.objects.filter(telegram_id=message.from_user.id).first()

    if temp_user is None:
        return False

    if temp_user.status == UserInfo.USER_STATUS[3][0]:
        return False

    if temp_user.status == UserInfo.USER_STATUS[0][0]:
        if check_login(message.text):
            temp_user.panel_id = message.text
            temp_user.status = UserInfo.USER_STATUS[1][0]
            bot.send_message(temp_user.telegram_id, "Пароль 1")

    elif temp_user.status == UserInfo.USER_STATUS[1][0]:
        if check_password_1(temp_user.panel_id, message.text):
            temp_user.codechkts = message.text
            temp_user.status = UserInfo.USER_STATUS[2][0]
            bot.send_message(temp_user.telegram_id, "Пароль 2")

    elif temp_user.status == UserInfo.USER_STATUS[2][0]:
        if check_password_2(temp_user.panel_id, temp_user.codechkts, message.text):
            temp_user.codechstate = message.text
            temp_user.status = UserInfo.USER_STATUS[3][0]
            bot.send_message(temp_user.telegram_id, f"Авторизовал")

    temp_user.save()
    return True


def user_handle_text(message):
    bot.send_message(message.from_user.id, "we are here!")
