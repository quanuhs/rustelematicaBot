import telebot
from telebot import types
from .api_handler import RustelematicaAPI

from .models import BotDictionary, UserInfo

import datetime
from datetime import timezone


class TelegramBot(telebot.TeleBot):
    def set_token(self, new_token):
        self.token = new_token


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




def handle_message(request, settings):
    bot.set_token(settings.token)
    api.set_api(settings.api_key)

    bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])




@bot.message_handler(commands=['start'])
def start(message):
    markup = Markups("RU")
    user = UserInfo.objects.filter(telegram_id=message.from_user.id).first()

    if user:
        if user.status == UserInfo.USER_STATUS[3][0]:
            bot.send_message(user.telegram_id, markup.text.menu_text, reply_markup=markup.start_menu())
            return
        else:
            user.delete()

    text_description = markup.text.welcome_text
    bot.send_message(message.from_user.id, text_description, reply_markup=markup.auth())



@bot.callback_query_handler(func=lambda call: call.data == "auth")
def callback_login(call: telebot.types.CallbackQuery):
    markup = Markups("RU")
    user, created = UserInfo.objects.get_or_create(telegram_id=call.from_user.id, name=call.from_user.username or "unknown")
    if not created:
        user.status = UserInfo.USER_STATUS[0][0]
        user.save()

    bot.send_message(call.message.chat.id, markup.text.auth_ask_panel_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)



@bot.message_handler(content_types=['text'])
def handle_text(message):
    markup = Markups("RU")
    if temp_handle_text(message, markup):
        return

    if user_handle_text(message, markup):
        return

    bot.send_message(message.from_user.id, markup.text.auth_text, reply_markup=markup.auth())



def temp_handle_text(message, markup:Markups):
    temp_user: UserInfo = UserInfo.objects.filter(telegram_id=message.from_user.id).first()

    if temp_user is None:
        return False

    if temp_user.status == UserInfo.USER_STATUS[3][0]:
        return False

    error_message = None

    if temp_user.status == UserInfo.USER_STATUS[0][0]:
        if api.check_panel_id(message.text) is None:
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
        data = api.check_codechstate(temp_user.panel_id, message.text)
        if data is None:
            error_message = markup.text.auth_fail_codechstate
        else:
            temp_user.codechstate = message.text
            temp_user.status = UserInfo.USER_STATUS[3][0]
            temp_user.object_uuid = data.get("idobject")
            bot.send_message(temp_user.telegram_id, markup.text.auth_success, reply_markup=markup.start_menu())

    if error_message:
        bot.send_message(temp_user.telegram_id, error_message, reply_markup=markup.auth())
        temp_user.delete()
        return True

    temp_user.save()

    return True



@bot.callback_query_handler(func=lambda call: call.data == "yes" or call.data == "no")
def start_test(call):
    markup = Markups("RU")
    user: UserInfo = UserInfo.objects.filter(telegram_id=call.from_user.id, status=UserInfo.USER_STATUS[3][0]).first()
    if user is None:
        return
    
    if call.data == "yes":
        try:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        except:
            bot.send_message(user.telegram_id, markup.text.ask_turn_cmd2, reply_markup=markup.agree_or_not())
            return
        
        if api.set_test_mode(user.panel_id, user.object_uuid, 0, True).get("servicemode"):
            user.service_time = datetime.datetime.now(timezone.utc)
            user.save()
            bot.send_message(user.telegram_id, markup.text.test_is_on)
        else:
            bot.send_message(user.telegram_id, markup.text.test_error)
    
    else:
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(e)



def check_system(user, markup:Markups):
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
    
    

def user_handle_text(message, markup:Markups):
    user: UserInfo = UserInfo.objects.filter(telegram_id=message.from_user.id, status=UserInfo.USER_STATUS[3][0]).first()
    markup = Markups("RU")

    if user is None:
        return False
    
    if message.text == markup.text.menu_btn_check:
        check_system(user, markup)
            
    
    elif message.text == markup.text.menu_btn_status:
        if api.get_data(1, user.panel_id, user.object_uuid).get("guardstate"):
            _text = markup.text.area_secure
        else:
            _text = markup.text.area_insecure
        bot.send_message(user.telegram_id, _text)
    
    
    
    elif message.text == markup.text.menu_btn_logout:
        msg = bot.send_message(user.telegram_id, "logout", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user.telegram_id, markup.text.auth_text, reply_markup=markup.auth())
        bot.delete_message(user.telegram_id, msg.message_id)
        user.delete()
        

    return True
