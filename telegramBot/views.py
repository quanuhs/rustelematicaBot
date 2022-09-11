import json

from django.http import HttpResponse
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from .logic import handle_message

from .models import BotSettings


@csrf_exempt
def handle_telegram(request, secret_key):
    settings = BotSettings.objects.filter(webhook_secret=secret_key).first()
    if settings is None:
        return HttpResponse("API key is invalid!", content_type="text/plain", status=403)

    handle_message(request, settings.token)

    return HttpResponse('OK', content_type="text/plain", status=200)
