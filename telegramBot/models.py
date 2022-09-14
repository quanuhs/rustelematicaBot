from operator import mod
from django.db import models


# Create your models here.

class BotSettings(models.Model):
    """Модель настройки Telegram бота"""

    bot_url = models.CharField(max_length=64, verbose_name="Ссылка на бота")
    token = models.CharField(max_length=128, verbose_name="Токен бота")
    api_key = models.CharField(max_length=128, verbose_name="API ключ")
    webhook_secret = models.CharField(max_length=128, verbose_name="Код webhook")

    def __str__(self):
        return f"{self.webhook_secret}"

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"


class UserInfo(models.Model):
    telegram_id = models.CharField(verbose_name="id пользователя в Telegram", max_length=16)
    name = models.CharField(verbose_name="Имя пользователя в Telegram", max_length=32)

    panel_id = models.IntegerField(verbose_name="panelid для работы с API", null=True)
    codechkts = models.TextField(verbose_name="codechkts для работы с API", null=True)
    codechstate = models.TextField(verbose_name="codechstate для работы с API", null=True)
    object_uuid = models.TextField(verbose_name="object_uuid для работы с API", null=True)
    service_time = models.DateTimeField(verbose_name="Время начала тестирования", null=True)

    USER_STATUS = (
        ('pending_login', 'Ожидаем ввода логина'),
        ('pending_password_1', 'Ожидаем ввод codechkts'),
        ('pending_password_2', 'Ожидаем ввод codechstate'),
        ('active', "Авторизованный")
    )

    status = models.CharField(choices=USER_STATUS, max_length=32, verbose_name='Статус', default=USER_STATUS[0][0])

    def __str__(self):
        return f"{self.telegram_id} | {self.name} > {self.panel_id}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class BotDictionary(models.Model):
    """Модель названий, используемых в Telegram боте"""
    language = models.CharField(max_length=16, default='RU', verbose_name='Язык справочника', unique=True)

    welcome_text = models.TextField(verbose_name="Текст приветствия /start")
    auth_text = models.TextField(verbose_name="Текст запроса авторизации")
    auth_success = models.TextField(verbose_name="Текст успешной авторизации")

    auth_ask_panel_id = models.TextField(verbose_name="Текст запроса panelid")
    auth_fail_panel_id = models.TextField(verbose_name="Текст неверного panelid")

    auth_ask_codechkts = models.TextField(verbose_name="Текст запроса codechkts")
    auth_ask_codechstate = models.TextField(verbose_name="Текст запроса codechstate")
    auth_fail_codechkts = models.TextField(verbose_name="Текст неверного codechkts")
    auth_fail_codechstate = models.TextField(verbose_name="Текст неверного codechstate")

    menu_text = models.TextField(verbose_name="Текст главного меню")

    menu_btn_check = models.CharField(max_length=128, verbose_name="Кнопка - тревожная кнопка")
    menu_btn_status = models.CharField(max_length=128, verbose_name="Кнопка - статус объекта")
    menu_btn_logout = models.CharField(max_length=128, verbose_name="Кнопка - выйти")
    menu_btn_login = models.CharField(max_length=128, verbose_name="Кнопка - авторизоваться")

    error_no_command = models.TextField(verbose_name="Текст неизвестной команды")
    area_secure = models.TextField(verbose_name="Текст - объект на охране")
    area_insecure = models.TextField(verbose_name="Текст - объекта не на охране")
    
    ask_turn_cmd2 = models.TextField(verbose_name="Текст (вопрос) - запустить режим тестирования")
    test_is_on = models.TextField(verbose_name="Текст включения тестирования")
    
    confirm_btn_yes = models.CharField(max_length=128, verbose_name="Кнопка - согласия/подтверждения")
    confirm_btn_no = models.CharField(max_length=128, verbose_name="Кнопка - отказа/отмены")
    
    alert_pressed = models.TextField(verbose_name="Текст - тревожная кнопка нажата")
    alert_not_pressed = models.TextField(verbose_name="Текст - тревожная кнопка не нажата")

    
    

    def __str__(self):
        return f"{self.language}"

    class Meta:
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"
