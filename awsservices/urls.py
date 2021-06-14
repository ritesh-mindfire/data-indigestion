from django.urls import path
from awsservices.views import SignS3RequestAPIView
from awsservices.views import direct_s3_upload_view
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('api/aws/sign-s3-request/', SignS3RequestAPIView.as_view(), name='aws-sign-s3-request/'),
    path('aws/direct-s3-upload/', direct_s3_upload_view, name='aws-direct-s3-upload/'),
]

urlpatterns = format_suffix_patterns(urlpatterns)