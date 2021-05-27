from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from accounts import tasks
from accounts.models import Manufacturer

import logging
logger = logging.getLogger('quickstart')

# Create your views here.

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# print(CACHE_TTL)

def dashboard(request):
    tasks.task_json_file_process()

    if 'mydata' in cache:
        # get results from cache
        manufacturers = cache.get('mydata')
        logger.info('Fetched from cache data {}'.format(manufacturers))

    else:
        manufacturers = Manufacturer.objects.all()
        manufacturers = list(manufacturers.values('id')[:5])
        cache.set('mydata', manufacturers)
        logger.info('Fetched from Database {}'.format(manufacturers))

    ctx = {'manufacturers': manufacturers}
    return render(request, 'dashboard.html', ctx)
    # return HttpResponse("Hello, world. You're at the dashboard. Total records: {}".format(manufacturers))