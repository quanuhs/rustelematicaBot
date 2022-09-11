from django.contrib import admin

# Register your models here.
from telegramBot.models import BotDictionary, BotSettings

@admin.register(BotDictionary)
class BotDictionaryAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Локализация', {
            'fields': ('language')
        }),
        ('Авторизация', {
            'fields': ('auth_text', 'auth_success', 'auth_ask_login', 'auth_fail_login', 'auth_ask_password',
                       'auth_fail_password', 'menu_btn_login')
        }),
        ('Основное меню', {
            'fields': ('menu_text', 'menu_btn_check', 'menu_btn_status', 'menu_btn_logout')
        }),
        ('Прочее', {
            'fields': ('welcome_text', 'error_no_command')
        })
    )