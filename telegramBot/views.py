import json

from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.

def handle_telegram(request, secret_key):
    data = request.body.decode('utf-8')
    #data = json.loads(request.body.decode('utf-8'))

    if 'callback_query' in data:
        #messages.handler_call_back(data)
        pass

    elif 'message' in data:
        pass

    return HttpResponse('ok', content_type="text/plain", status=200)
