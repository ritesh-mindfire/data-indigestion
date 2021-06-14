from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import Manufacturer, UploadFile

from django.contrib.auth import get_user_model
User = get_user_model()
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at']

@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = ['image',]

