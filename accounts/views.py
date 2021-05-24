from django.shortcuts import render
from django.http import HttpResponse
from accounts import tasks
from accounts.models import Manufacturer

# Create your views here.


def dashboard(request):
    tasks.task_json_file_process()
    return HttpResponse("Hello, world. You're at the dashboard.")