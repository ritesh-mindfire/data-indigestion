import csv
import os
from datetime import datetime

import pdfkit
import xlsxwriter
from django.conf import settings
from django.db.models import Count
from django.db.models import Sum
from django.template.loader import render_to_string

from accounts.models import Manufacturer


def create_pdf_report():
    all_obj = Manufacturer.objects.filter(created_at__date=datetime.today().date())
    record_data = all_obj.values('country', 'name').annotate(cnt=Count('id'), total_price=Sum('price'))
    
    data = render_to_string('report.html', {'record_data': record_data})

    report_name = "{}.pdf".format(datetime.today().date().strftime("%Y-%m-%d"))
    report_path = os.path.join(settings.MEDIA_UPLOAD_PATH, report_name)
    
    pdfkit.from_string(data, report_path)

    return report_path


def create_csv_report():
    all_obj = Manufacturer.objects.filter(created_at__date=datetime.today().date())
    record_data = all_obj.values('country', 'name').annotate(cnt=Count('id'), total_price=Sum('price'))

    report_name = "{}.csv".format(datetime.today().date().strftime("%Y-%m-%d"))
    report_path = os.path.join(settings.MEDIA_UPLOAD_PATH, report_name)

    with open(report_path, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['Country', 'Manufacturer', 'Car Manufactured', 'Total Price'])

        for record in record_data:
            writer.writerow([record['country'],
                            record['name'],
                            record['cnt'],
                            record['total_price']])
    
    return report_path


def create_excel_report():
    all_obj = Manufacturer.objects.filter(created_at__date=datetime.today().date())
    record_data = all_obj.values('country', 'name').annotate(cnt=Count('id'), total_price=Sum('price'))

    report_name = "{}.xlsx".format(datetime.today().date().strftime("%Y-%m-%d"))
    report_path = os.path.join(settings.MEDIA_UPLOAD_PATH, report_name)

    workbook = xlsxwriter.Workbook(report_path)
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})

    headers = ['Country', 'Manufacturer', 'Car Manufactured', 'Total Price']
    for col_num, col_data in enumerate(headers):
        worksheet.write(0, col_num, col_data, bold)

    for row, record in enumerate(record_data):
        row_data = [record['country'], record['name'], record['cnt'], record['total_price']]
        for col_num, col_data in enumerate(row_data):
            worksheet.write(row+1, col_num, col_data)

    workbook.close()

    return report_path