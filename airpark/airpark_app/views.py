from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['POST'])
def create_user(request):
    return JsonResponse({'message' : 'hello'})
