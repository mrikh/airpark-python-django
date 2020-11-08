from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password

from rest_framework.parsers import JSONParser
from .models import *
from .serializers import *
from rest_framework.exceptions import ValidationError

# Create your views here.
@api_view(['POST'])
def create_user(request):

    body = JSONParser().parse(request)
    try:
        user_serializer = UserSerializer(data=body)
        if user_serializer.is_valid(raise_exception = True):
            user = user_serializer.save()
            data = user_serializer.data
            del data['password']
            return JsonResponse({"code" : 200, 'data': data, 'message' : 'Success'})
    except ValidationError as e:
        return JsonResponse({"code" : e.status_code, 'message' : e.detail})


@api_view(['POST'])
def login_user(request):

    body = JSONParser().parse(request)
    try:
        user = User.objects.get(email=body['email'].strip())
        if check_password(body['password'], user.password):
            jsonData = UserSerializer(user, many = False).data
            del jsonData['password']
            return JsonResponse({"code" : 200, 'data': jsonData, 'message' : 'Success'})
        else:
            return JsonResponse({"code" : 400, 'message' : 'Password doesnt match'})
    except User.DoesNotExist:
        return JsonResponse({"code" : 400, 'message' : 'User not found'})