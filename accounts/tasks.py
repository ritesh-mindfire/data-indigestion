import os, json, csv
from celery import shared_task
from django.conf import settings
from accounts.models import Manufacturer
from datetime import date, datetime
from django.db.models import Count, Sum


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def task_json_file_process():
    folder_path = os.path.join(settings.MEDIA_DOWNLOAD_PATH,'2021-05-20')
    dir_list = os.listdir(folder_path)

    success, failure = 0, 0

    for filename in dir_list:
        filepath = os.path.join(folder_path,filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as exc:
            failure += 1
            continue
        
        success += 1
        for data_dct in data:
            # print(data_dct)
            # print('--------------------------------------------------')
            manufacturer_dct = {
                'name': data_dct.get('Manufacturer', ''),
                'car_model' : data_dct.get('Model', ''),
                'car_year' : data_dct.get('ModelYear', ''),
                'country' : data_dct.get('Country', ''),
                'price' : data_dct.get('Price', ''),
            }

            try:
                obj = Manufacturer.objects.create(**manufacturer_dct)
            except Exception as exc:
                pass

    # Start report creation
    all_obj = Manufacturer.objects.filter(created_at__date=datetime.today().date())
    record_data = all_obj.values('country', 'name').annotate(cnt=Count('id'), total_price=Sum('price'))
    report_path = os.path.join(settings.MEDIA_DOWNLOAD_PATH,'report.csv')
    with open(report_path, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['Country', 'Manufacturer', 'Car Manufactured', 'Total Price'])

        for record in record_data:
            writer.writerow([record['country'],
                            record['name'],
                            record['cnt'],
                            record['total_price']])



