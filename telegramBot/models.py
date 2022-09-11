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

    panel_id = models.IntegerField(verbose_name="panelid для работы с API")
    codechkts = models.TextField(verbose_name="codechkts для работы с API")
    codechstate = models.TextField(verbose_name="codechstate для работы с API")
    object_uuid = models.TextField(verbose_name="object_uuid для работы с API")
    service_time = models.DateTimeField(verbose_name="Время начала тестирования")

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

    auth_ask_login = models.TextField(verbose_name="Текст запроса логина")
    auth_fail_login = models.TextField(verbose_name="Текст неврного логина")

    auth_ask_password = models.TextField(verbose_name="Текст запроса пароля")
    auth_fail_password = models.TextField(verbose_name="Текст неверного пароля")

    menu_text = models.TextField(verbose_name="Текст главного меню")

    menu_btn_check = models.TextField(verbose_name="Кнопка - тревожная кнопка")
    menu_btn_status = models.TextField(verbose_name="Кнопка - статус объекта")
    menu_btn_logout = models.TextField(verbose_name="Кнопка - выйти")
    menu_btn_login = models.TextField(verbose_name="Кнопка - авторизоваться")

    error_no_command = models.TextField(verbose_name="Текст неизвестной комманды")

    def __str__(self):
        return f"{self.language}"

    class Meta:
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"
