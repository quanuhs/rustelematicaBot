import json

from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from messages import handle_message


@csrf_exempt
def handle_telegram(request, secret_key):
    handle_message(request)

    return HttpResponse('ok', content_type="text/plain", status=200)
