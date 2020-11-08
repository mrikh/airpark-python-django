from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.decorators import api_view

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
            user_serializer.save()
            return JsonResponse({"code" : 200, 'data': body, 'message' : 'Success'})
    except ValidationError as e:
        return JsonResponse({"code" : e.status_code, 'message' : e.detail})