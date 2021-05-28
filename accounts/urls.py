from django.urls import path
from accounts import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/manufacturers_list/', views.manufacturers_list, name='manufacturers_list'),
    path('api/manufacturers/', views.ManufacturersList.as_view()),
    path('api/manufacturers/<int:pk>/', views.ManufacturerDetail.as_view()),
    path('api/manufacturers/<int:pk>/edit/', views.ManufacturerUpdate.as_view()),
    path('api/userinfo/', views.UserInfo.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)