from datetime import datetime
from accounts import serializers
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser


from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models import Count
from django.db.models.functions import Cast
from django.db.models.fields import DateField

from django.contrib.auth import get_user_model
User = get_user_model()


from accounts import tasks
from accounts.serializers import ManufacturerModelSerializer, UserSerializer
from accounts.models import Manufacturer

import logging
logger = logging.getLogger('quickstart')

# Create your views here.

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# print(CACHE_TTL)

def dashboard(request):
    # tasks.task_data_processing_and_report_creation.delay()

    if 'country_data' in cache:
        # get results from cache
        record_data = cache.get('country_data')
        # logger.info('Fetched from cache data {}'.format(manufacturers))

    else:
        manufacturers = Manufacturer.objects.filter(created_at__year=datetime.now().year)
        record_data = manufacturers.values('country').annotate(cnt=Count('id')).values('country', 'cnt')
        cache.set('country_data', record_data)
        # logger.info('Fetched from Database {}'.format(manufacturers))

    qs = Manufacturer.objects.filter()
    records = qs.annotate(date_only=Cast('created_at', DateField())
                                ).values('date_only','name'
                                ).annotate(cnt=Count('id')
                                ).order_by('date_only'
                                ).values('date_only', 'name', 'cnt')

    dates = []
    country_data = {}
    for record in records:
        c_name = record['name']
        if c_name in country_data:
            country_data[c_name].append(record['cnt'])
        else:
            country_data[c_name] = [record['cnt']]

        if record['date_only'] not in dates:
            dates.append(record['date_only'])

    monthly_record = {
        'dates': dates,
        'records': list(country_data.items())
    }
        
    ctx = {'record_data': record_data, 'monthly_record': monthly_record}
    return render(request, 'dashboard.html', ctx)



# Function based view
def manufacturers_list(request):
    if request.method == 'GET':
        manufacturers = Manufacturer.objects.filter(created_at__date = datetime.today().date())[:10]
        serializer = ManufacturerModelSerializer(manufacturers, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ManufacturerModelSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


# Class based APIView
class ManufacturersList(APIView):
    def get(self, request, format=None):
        manufacturers = Manufacturer.objects.filter(created_at__date = datetime.today().date())[:10]
        serializer = ManufacturerModelSerializer(manufacturers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ManufacturerModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Class based APIView Mixin
class ManufacturerDetail(mixins.RetrieveModelMixin,
                    # mixins.UpdateModelMixin,
                    # mixins.DestroyModelMixin,
                    generics.GenericAPIView):

    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerModelSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


# Class based APIView Generics
class ManufacturerUpdate(generics.UpdateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerModelSerializer


class UserInfo(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            user = User.objects.get(username=username)

            response = self.serializer_class(user)
            return Response(response.data, status=status.HTTP_200_OK)   
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

