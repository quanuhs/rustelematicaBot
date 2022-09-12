from django.contrib import admin

# Register your models here.
from telegramBot.models import BotDictionary, BotSettings, UserInfo


@admin.register(BotDictionary)
class BotDictionaryAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Авторизация', {
            'fields': ['auth_text', 'auth_success', 'auth_ask_panel_id', 'auth_fail_panel_id', 'auth_ask_codechkts',
                       'auth_fail_codechkts', 'auth_ask_codechstate', 'auth_fail_codechstate', 'menu_btn_login']
        }),
        ('Главное меню', {
            'fields': ['menu_text', 'menu_btn_check', 'menu_btn_status', 'menu_btn_logout']
        }),
        ('Прочее', {
            'fields': ['welcome_text', 'error_no_command']
        })
    )
    exclude = ['language']


@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    pass


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    pass

admin.site.site_header = 'RustelematicaBot Panel'