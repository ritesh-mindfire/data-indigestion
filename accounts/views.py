from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from accounts import tasks
from accounts.models import Manufacturer

# Create your views here.

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
print(CACHE_TTL)

def dashboard(request):
    tasks.task_json_file_process()

    if 'manufacturers' in cache:
        # get results from cache
        manufacturers = cache.get('data')

    else:
        manufacturers = Manufacturer.objects.all()
        cache.set('data', manufacturers, timeout=CACHE_TTL)

    return HttpResponse("Hello, world. You're at the dashboard. Total records: {}".format(manufacturers.count()))