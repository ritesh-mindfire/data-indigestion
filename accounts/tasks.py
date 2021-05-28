import csv
import json
import os
from datetime import datetime

import openpyxl
from celery import shared_task

from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Count
from django.db.models import Sum

from accounts import report
from accounts.models import Manufacturer


@shared_task(name='custom_add')
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
    failure_files = []

    for filename in dir_list:
        filepath = os.path.join(folder_path,filename)

        if filename.lower().endswith('.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except Exception as exc:
                failure += 1
                failure_files.append(filename)
                continue
            
            success += 1
            process_data_into_db(data)

        elif filename.lower().endswith('.csv'):
            data = []
            try:
                with open(filepath, 'r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
            except Exception as exc:
                failure += 1
                failure_files.append(filename)
                continue

            success += 1
            process_data_into_db(data)
        
        elif filename.lower().endswith('.xlsx'):
            data = []
            try:
                wb_obj = openpyxl.load_workbook(filepath) 
                # Read the active sheet:
                sheet = wb_obj.active
            except Exception as exe:
                failure += 1
                failure_files.append(filename)
                continue
            
            headers = ()
            for i, row in enumerate(sheet.iter_rows(values_only=True)):
                if i == 0:
                    headers = row
                    continue
                data.append(dict(zip(headers, row)))
            
            success += 1
            process_data_into_db(data)

        else:
            failure_files.append(filename)
            failure += 1
            continue

    # Start report creation
    csv_filepath = report.create_csv_report()
    pdf_filepath = report.create_pdf_report()
    xlsx_filepath = report.create_excel_report()    

    # TODO:  upload report back to Drive Folder Reports
        
    # email sending post file processing
    task_send_daily_job_status_email(success, failure, failure_files)


def process_data_into_db(data: list) -> None:
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


@shared_task
def task_send_daily_job_status_email(success, failure, failure_files):
    
    subject = "Daily status report for {}".format(datetime.today().date().strftime("%Y-%m-%d"))
    message = """Hi All, 
    Please refer below daily status report.

        Total Report count: {}
        Success Report Count: {}

        Failure Report Count: {}
        Files not processed: {}
        
        
    Regards,
    Mindfire Team""".format(success+failure, success, failure, failure_files)
    recipient_list = ['ritesh.g@mindfiresolutions.com' ]

    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        bcc=[],
    )
    email.send(fail_silently=False)
