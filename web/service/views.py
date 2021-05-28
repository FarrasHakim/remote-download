from django.shortcuts import render
from django.http import HttpResponse

import pika

def index(request):
    if request.method == 'POST':
        return HttpResponse("Hello There")
    return render(request, "index.html")
