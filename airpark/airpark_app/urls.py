from django.conf.urls import url 
from . import views
 
urlpatterns = [ 
    url(r'^api/create-user', views.create_user),
    url(r'^api/login-user', views.login_user),
    url(r'^api/ephemeral-key', views.ephemeral_key),
    url(r'^api/payment-intent', views.payment_intent),
    url(r'^api/airports-list', views.airports_list),
    url(r'^api/availability-list', views.get_availability),
    url(r'^api/post-price', views.post_price)
]