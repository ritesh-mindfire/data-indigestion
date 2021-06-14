import csv
import json
import os
from datetime import datetime

import openpyxl
from celery import shared_task

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.db.models import Count
from django.db.models import Sum


from accounts import report
from accounts.models import Manufacturer
from gdrive_service.gdrive import GDriveService

import logging
logger = logging.getLogger('quickstart')


@shared_task(name='custom_add')
def add(x, y):
    return x + y


@shared_task    
def mul(x, y):
    return x * y


@shared_task(name='task_data_processing_and_report_creation')
def task_data_processing_and_report_creation():
    logger.info('**'*25)
    logger.info('Start task for file processing and report creation')
    folder_path = os.path.join(settings.MEDIA_DOWNLOAD_PATH, datetime.today().strftime("%Y-%m-%d"))
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    gdrive_instance = GDriveService(folder_path)

    folder_id = gdrive_instance.fetch_drive_folders('Manufacture Data')
    if folder_id:
        gdrive_instance.fetch_drive_folder_files(folder_id)
    else:
        logger.info("Folder name does not exist with name 'Manufacture Data'")
        return None
    
    dir_list = os.listdir(folder_path)
    if not dir_list:
        logger.info('No file received for processing today')
        task_send_daily_nofile_email()
        return None

    success, failure = 0, 0
    failure_files = []

    logger.info('File processing fetched from Drive (%s)' % dir_list)
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
    logger.info('Prepare data from DB for report creation')
    all_obj = Manufacturer.objects.filter(created_at__date=datetime.today().date())
    record_data = all_obj.values('country', 'name').annotate(cnt=Count('id'), total_price=Sum('price'))

    logger.info('Prepare report for data fetched from DB')
    csv_filepath = report.create_csv_report(record_data)
    pdf_filepath = report.create_pdf_report(record_data)
    xlsx_filepath = report.create_excel_report(record_data)

    # upload report back to Drive Folder Reports
    folder_id = gdrive_instance.fetch_drive_folders('Report')
    if not folder_id:
        folder_id = gdrive_instance.create_drive_folder('Report')

    logger.info('Uploading report file to Drive')
    gdrive_instance.upload_drive_files(folder_id, csv_filepath)
    gdrive_instance.upload_drive_files(folder_id, pdf_filepath)
    gdrive_instance.upload_drive_files(folder_id, xlsx_filepath)
    logger.info('Uploading report file to Drive completed')

    # email sending post file processing
    task_send_daily_job_status_email(success, failure, failure_files)


def process_data_into_db(data: list) -> None:
    for data_dct in data:

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


@shared_task
def task_send_daily_nofile_email():
    
    ctx = {'today_date': datetime.today().strftime("%Y-%m-%d")}
    subject = "Daily status report for {}".format(ctx['today_date'])
    message = render_to_string('email_templates/daily_report_failure.txt', ctx)
    recipient_list = ['ritesh.g@mindfiresolutions.com' ]

    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        bcc=[],
    )
    email.send(fail_silently=False)
