from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')
        
    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.email = user.email.strip()
        user.name = user.name.strip()
        user.password = make_password(user.password)
        user.save()
        return user

class BookingSerializer(serializers.ModelSerializer):

    stripe_customer_id = serializers.CharField(source = 'customer_id')
    user_email = serializers.CharField(source = 'email')
    booking_start_date = serializers.DateTimeField(source = 'start_date')
    booking_end_date = serializers.DateTimeField(source = 'end_date')

    class Meta:
        model = Booking

class CarParkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarPark
        fields = ('id', 'airport_id', 'airport_name', 'image', 'car_park_name', 'price', 'latitude', 'longitude', 'dis_capacity', 'normal_capacity', 'tw_capacity', 'is_long_term')