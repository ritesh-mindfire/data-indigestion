from django.conf import settings
from rest_framework import serializers
from datetime import date, datetime

from accounts.models import Manufacturer
from django.contrib.auth import get_user_model
User = get_user_model()

# class ManufacturerSerializer(serializers.Serializer):
#     name = serializers.CharField(max_length=64)
#     car_model = serializers.CharField(max_length=64)
#     car_year = serializers.IntegerField(default=2021)
#     country = serializers.CharField(max_length=64, default='maruti')
#     price = serializers.FloatField(default=250000)

#     def create(self, validated_data):
#         return Manufacturer.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.car_model = validated_data.get('car_model', instance.car_model)
#         instance.save()
#         return instance

    
class ManufacturerModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        # fields = ['name', 'car_model', 'car_year', 'country']
        fields = '__all__'
        

    def validate_car_year(self, value):
        if value > datetime.now().year:
            raise serializers.ValidationError("Year cannot be in Future")
        return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4}}
        read_only_fields = ['id', 'email']

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        try:
            user = User.objects.get(username=username)
        except Exception as exc:
            raise serializers.ValidationError("Username doesnot Exists")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Password doesnot Match")

        return data
