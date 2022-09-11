import telebot
from telebot import types
from .api_handler import RustelematicaAPI

from .models import BotDictionary, UserInfo


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
        keyboard.row(self.text.menu_btn_logout)
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
    markup = Markups("RU")
    user, created = UserInfo.objects.get_or_create(telegram_id=message.from_user.id, name=message.from_user.username or "unknown")

    if not created:
        bot.send_message(user.telegram_id, markup.text.menu_text, reply_markup=markup.start_menu())
        return

    text_description = markup.text.welcome_text
    bot.send_message(message.from_user.id, text_description, reply_markup=markup.auth())


@bot.callback_query_handler(func=lambda call: call.data == "auth")
def callback_login(call: telebot.types.CallbackQuery):
    markup = Markups("RU")
    bot.send_message(call.message.chat.id, markup.text.auth_ask_panel_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if temp_handle_text(message):
        return

    if user_handle_text(message):
        return

    start(message)


def temp_handle_text(message):
    temp_user: UserInfo = UserInfo.objects.filter(telegram_id=message.from_user.id).first()
    markup = Markups("RU")

    if temp_user is None:
        return False

    if temp_user.status == UserInfo.USER_STATUS[3][0]:
        return False

    error_message = None

    if temp_user.status == UserInfo.USER_STATUS[0][0]:
        if api.check_panel_id(int(message.text)) is None:
            error_message = markup.text.auth_fail_panel_id
        else:
            temp_user.panel_id = int(message.text)
            temp_user.status = UserInfo.USER_STATUS[1][0]
            bot.send_message(temp_user.telegram_id, markup.text.auth_ask_codechkts)

    elif temp_user.status == UserInfo.USER_STATUS[1][0]:
        if api.check_codechkts(temp_user.panel_id, message.text) is None:
            error_message = markup.text.auth_fail_codechkts
        else:
            temp_user.codechkts = message.text
            temp_user.status = UserInfo.USER_STATUS[2][0]
            bot.send_message(temp_user.telegram_id, markup.text.auth_ask_codechstate)

    elif temp_user.status == UserInfo.USER_STATUS[2][0]:
        if api.check_codechstate(temp_user.panel_id, message.text) is None:
            error_message = markup.text.auth_fail_codechstate
        else:
            temp_user.codechstate = message.text
            temp_user.status = UserInfo.USER_STATUS[3][0]
            bot.send_message(temp_user.telegram_id, markup.text.auth_success, reply_markup=markup.start_menu())

    if error_message:
        bot.send_message(temp_user.telegram_id, error_message, reply_markup=markup.auth())
        temp_user.delete()
        return True

    temp_user.save()

    return True


def user_handle_text(message):
    temp_user: UserInfo = UserInfo.objects.filter(telegram_id=message.from_user.id).first()
    markup = Markups("RU")

    if temp_user is None:
        return False

    return True
