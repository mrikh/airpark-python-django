from django.conf.urls import url 
from . import views
 
urlpatterns = [ 
    url(r'^api/create-user', views.create_user),
    url(r'^api/login-user', views.login_user),
    url(r'^api/payment-intent', views.payment_intent),
    url(r'^api/airports-list', views.airports_list),
    url(r'^api/availability-list', views.get_availability),
    url(r'^api/calc-price', views.calc_price),
    url(r'^api/payment-done', views.payment_done)
]