from ast import Return
import telebot
from telebot import types
from .api_handler import RustelematicaAPI

from .models import BotDictionary, BotSettings, UserInfo

import datetime
from datetime import date, timezone
import asyncio



class TelegramBot(telebot.TeleBot):
    settings = None
    
    def set_token(self, new_token):
        self.token = new_token
    
    def set_settings(self, settings):
        self.settings = settings


bot: TelegramBot = TelegramBot(None)
api: RustelematicaAPI = RustelematicaAPI(None)


class Markups:
    def __init__(self, language):
        self.language = language

    @property
    def text(self) -> BotDictionary:
        return BotDictionary.objects.filter(language=self.language).first()

    def start_menu(self):
        keyboard = types.ReplyKeyboardMarkup(True, False)
        keyboard.row(self.text.menu_btn_status, self.text.menu_btn_check)
        keyboard.row(self.text.menu_btn_logout)
        return keyboard

    def auth(self):
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text=self.text.menu_btn_login, callback_data="auth")
        keyboard.add(button)
        return keyboard
    
    def agree_or_not(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text=self.text.confirm_btn_yes, callback_data="yes"))
        keyboard.add(types.InlineKeyboardButton(text=self.text.confirm_btn_no, callback_data="no"))
        return keyboard
    

async def check_test_button(user: UserInfo, button_pressed_text, button_not_pressed_text, sleep_time_sec:float=3.0, times: int=3):
    _text = button_not_pressed_text
    for i in range(times):
        if not is_auth_user(user):
            return
        
        if api.check_test(1, user.panel_id, user.object_uuid, user.service_time, 1201):
            _text = button_pressed_text
            break
        else:
            await asyncio.sleep(sleep_time_sec)

    bot.send_message(user.telegram_id, _text)
    return True
    


def is_auth_user(user:UserInfo):
    if user is None:
        return False

    if user.status != UserInfo.USER_STATUS[3][0]:
        return False
    
    if not api.validate_user_data(user.panel_id, user.codechkts, user.codechstate):
        user.change_status(None)
        return False

    return True


def handle_message(request, _settings):
    bot.set_token(_settings.token)
    bot.set_settings(_settings)
    api.set_api(_settings.api_key)

    bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])


def is_user_banned(user:UserInfo):
    if user is None:
        return False

    settings = bot.settings
    if settings is None:
        return

    if user.errors_before_ban >= settings.allowed_tries:
        user.change_status(UserInfo.USER_STATUS[4][0])
        user.ban_time = datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=5)
        user.clear_data()
        user.save()

    if user.status != UserInfo.USER_STATUS[4][0]:
        return False
    
    if user.ban_time is None:
        return False
    
    time_differ = user.ban_time - datetime.datetime.now(tz=timezone.utc)
    if time_differ.total_seconds() <= 0:
        user.change_status(None)
        user.ban_time = None
        user.save()
        return False

    return True
    

@bot.message_handler(commands=['start'])
def start(message):
    markup = Markups("RU")
    user: UserInfo = UserInfo.objects.filter(telegram_id=message.from_user.id).first()


    if is_auth_user(user):
        bot.send_message(user.telegram_id, markup.text.menu_text, reply_markup=markup.start_menu())
        return

    if not is_user_banned(user):
        user.change_status(None)
        

    text_description = markup.text.welcome_text
    bot.send_message(message.from_user.id, text_description, reply_markup=markup.auth())


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: telebot.types.CallbackQuery):
    user, created = UserInfo.objects.get_or_create(telegram_id=call.from_user.id, name=call.from_user.username or "unknown")
    markup = Markups("RU")
    
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    

    if is_user_banned(user):
        bot.send_message(call.message.chat.id, get_ban_message(user, markup))
    
    elif call.data == "auth":
        user.change_status(UserInfo.USER_STATUS[0][0], False)
        ask_login(call.message.chat.id, markup)

    elif call.data == "yes":
        start_test(user, markup)
        
    elif call.data == "no":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    

def ask_login(chat_id, markup):
    bot.send_message(chat_id, markup.text.auth_ask_panel_id)

def get_ban_message(user:UserInfo, markup):
    time_differ = user.ban_time - datetime.datetime.now(tz=timezone.utc)
    _text = max(round(time_differ.total_seconds()), 0)
    return f"{markup.text.user_banned} {_text} {markup.text.user_banned_second}"

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user:UserInfo = UserInfo.objects.filter(telegram_id=message.from_user.id).exclude(status=None).first()
    markup = Markups("RU")
    
    if is_user_banned(user):
        bot.send_message(user.telegram_id, get_ban_message(user, markup))
        return
    
    
    if is_auth_user(user):
        user_handle_text(message, markup, user)
    
    if user is None or user.status == None:
        bot.send_message(message.from_user.id, markup.text.auth_text, reply_markup=markup.auth())
        return
    
    temp_handle_text(message, markup, user)
    
    if is_user_banned(user):
        bot.send_message(user.telegram_id, get_ban_message(user, markup))
    
        


def temp_handle_text(message, markup, temp_user):
    error_message = None

    if temp_user.status == UserInfo.USER_STATUS[0][0]:
        if api.check_panel_id(message.text) is None:
            error_message = markup.text.auth_fail_panel_id
        else:
            temp_user.panel_id = int(message.text)
            temp_user.change_status(UserInfo.USER_STATUS[1][0], False)
            bot.send_message(temp_user.telegram_id, markup.text.auth_ask_codechkts)

    elif temp_user.status == UserInfo.USER_STATUS[1][0]:
        if api.check_codechkts(temp_user.panel_id, message.text) is None:
            error_message = markup.text.auth_fail_codechkts
        else:
            temp_user.codechkts = message.text
            temp_user.change_status(UserInfo.USER_STATUS[2][0], False)
            bot.send_message(temp_user.telegram_id, markup.text.auth_ask_codechstate)

    elif temp_user.status == UserInfo.USER_STATUS[2][0]:
        data = api.check_codechstate(temp_user.panel_id, message.text)
        if data is None:
            error_message = markup.text.auth_fail_codechstate
        else:
            temp_user.codechstate = message.text
            temp_user.change_status(UserInfo.USER_STATUS[3][0], False)
            temp_user.object_uuid = data.get("idobject")
            bot.send_message(temp_user.telegram_id, markup.text.auth_success, reply_markup=markup.start_menu())

    if error_message:
        bot.send_message(temp_user.telegram_id, error_message, reply_markup=markup.auth())
        temp_user.errors_before_ban += 1

    temp_user.save()
    return True

def user_handle_text(message, markup, user):
    """
        Выполняется в случае, если пользователь авторизован
        Принимает message от telebot (сообщение Telegram)
        
        Проверяет сообщение на наличие команд и выполняет соответствующую команду
        Возвращает True, если удалось что-то сделать с входными данными и
        Возвращает False, если данные преднозначались не этой функции или с ними ничего не сделать
        
    """

    
    
    if message.text == markup.text.menu_btn_check:
        # Пользователь проверяет кнопку и/или переводит объект в режим тестирования
        check_system(user, markup)
            
    
    elif message.text == markup.text.menu_btn_status:
        # Пользователь проверяет статус объекта
    
        if api.get_data(1, user.panel_id, user.object_uuid).get("guardstate"):
            _text = markup.text.area_secure
        else:
            _text = markup.text.area_insecure
        bot.send_message(user.telegram_id, _text)
    
    
    elif message.text == markup.text.menu_btn_logout:
        # Пользователь выходит из системы
        msg = bot.send_message(user.telegram_id, "logout", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user.telegram_id, markup.text.auth_text, reply_markup=markup.auth())
        bot.delete_message(user.telegram_id, msg.message_id)
        user.delete()
        

    return True



def start_test(user, markup):
    """
    Переводит объект авторизованного пользователя в режим тестирования
    """
    
    if not is_auth_user(user):
        return False
    
    if api.set_test_mode(user.panel_id, user.object_uuid, 0, True).get("servicemode"):
        user.service_time = datetime.datetime.now(timezone.utc)
        user.save()
        bot.send_message(user.telegram_id, markup.text.test_is_on)
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        task = loop.create_task(check_test_button(user, markup.text.alert_pressed, markup.text.alert_not_pressed))
        loop.run_until_complete(task)
        loop.close()
    
    else:
        bot.send_message(user.telegram_id, markup.text.test_error)




def check_system(user:UserInfo, markup:Markups):
    """
    Проверяет тревожную кнопку объекта
    Если время последний запуск тестирования был более 4 минут назад
    --> Предлагает перверсти объект в режим тестирования
    
    """
    if not is_auth_user(user):
        return False
    
    if user.service_time is None:
            bot.send_message(user.telegram_id, markup.text.ask_turn_cmd2, reply_markup=markup.agree_or_not())
            return
        
    time_differ = datetime.datetime.now(tz=timezone.utc) - user.service_time
    
    if time_differ.total_seconds() >= 60*4:
        bot.send_message(user.telegram_id, markup.text.ask_turn_cmd2, reply_markup=markup.agree_or_not())
        return

    if api.check_test(1, user.panel_id, user.object_uuid, user.service_time, 1201):
        _text = markup.text.alert_pressed
    else:
        _text = markup.text.alert_not_pressed
        
    
    bot.send_message(user.telegram_id, _text)

