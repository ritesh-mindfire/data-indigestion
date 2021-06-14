import os, boto3

from django.http.response import HttpResponse
from botocore.exceptions import ClientError
from botocore.client import Config

from django.conf import settings
from django.shortcuts import render, redirect

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
        
AWS_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_S3_REGION_NAME = settings.AWS_S3_REGION_NAME


def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, 
                          expiration=3600):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client('s3', config=Config(signature_version='s3v4'), 
                                aws_access_key_id=AWS_ACCESS_KEY_ID, 
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                region_name=AWS_S3_REGION_NAME,)

    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        response = None

    # The response contains the presigned URL and required fields
    return response


class SignS3RequestAPIView(APIView):

    def get(self, request):
        file_name = request.query_params.get('file-name')
        file_type = request.query_params.get('file-type')
        if not file_name:
            return Response({'detail': '`file-name` is mandatory.'})

        fields = {
            # "Content-Type": file_type
        }
        conditions = [ 
            {"bucket": AWS_BUCKET_NAME}, 
            # {"acl": "public-read"},
            # {"Content-Type": file_type}
        ]
        presigned_post = create_presigned_post(AWS_BUCKET_NAME, file_name, fields=fields, conditions=conditions)
        
        return Response({
            'data': presigned_post,
            'url': 'https://%s.s3.amazonaws.com/%s' % (AWS_BUCKET_NAME, file_name)
        })


def direct_s3_upload_view(request):
    ctx = {}
    if request.method == 'GET':
        file_name = request.GET.get('file-name', 'temp')
        
        fields = {
            # "Content-Type": file_type
        }
        conditions = [ 
            {"bucket": AWS_BUCKET_NAME}, 
            # {"acl": "public-read"},
            # {"Content-Type": file_type}
        ]
        presigned_post = create_presigned_post(AWS_BUCKET_NAME, file_name, fields=fields, conditions=conditions)
        if not presigned_post:
            return HttpResponse('Unable to provide temporay access for file upload.')

        ctx.update({
            'url': presigned_post.get('url'),
            'key': presigned_post.get('fields', {}).get('key'),
            'algorithm': presigned_post.get('fields', {}).get('x-amz-algorithm'),
            'credential': presigned_post.get('fields', {}).get('x-amz-credential'),
            'date': presigned_post.get('fields', {}).get('x-amz-date'),
            'policy': presigned_post.get('fields', {}).get('policy'),
            'signature': presigned_post.get('fields', {}).get('x-amz-signature'),
        })

        return render(request, 'direct_s3_upload.html', ctx)
