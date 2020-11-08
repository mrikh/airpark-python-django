from django.conf.urls import url 
from . import views
 
urlpatterns = [ 
    url(r'^api/create-user', views.create_user),
]