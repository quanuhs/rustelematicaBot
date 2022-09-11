from django.db import models


# Create your models here.

class BotSettings(models.Model):
    """Модель настройки Telegram бота"""

    token = models.CharField(max_length=128, verbose_name="Токен бота")
    webhook_secret = models.CharField(max_length=128, verbose_name="Код webhook")

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"


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
