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
        user.password = make_password(user.password.strip())
        user.save()
        return user