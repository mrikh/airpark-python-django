from django.db import models
from django.core.validators import validate_email


# Create your models here.
class User(models.Model):

    # id added automatically
    name = models.CharField(max_length = 30, blank = False, default = '')
    password = models.CharField(max_length = 1000, blank = False, default = '')
    email = models.CharField(max_length = 50, blank = False, default = '', validators = [validate_email], unique = True)

    class Meta:
        db_table = 'Users'


class CarPark(models.Model):

    # id added automatically
    airport_name = models.CharField(max_length = 100, blank = False)
    airport_id = models.CharField(max_length = 100, blank = False)
    image = models.TextField(max_length = 10000, blank = False)
    car_park_name = models.CharField(max_length = 100, blank = False)
    price = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    dis_capacity = models.IntegerField()
    normal_capacity = models.IntegerField()
    tw_capacity = models.IntegerField()
    is_long_term = models.BooleanField()

    class Meta:
        db_table = 'CarPark'


class Booking(models.Model):

    car_park = models.ForeignKey(CarPark, on_delete = models.DO_NOTHING)
    email = models.CharField(max_length = 50, blank = False, default = '', validators = [validate_email])
    is_old = models.BooleanField(default = False)
    is_logged_in = models.BooleanField(default = False)
    car_wash = models.BooleanField(default = False)
    is_handicap = models.BooleanField(default = False)
    start_date = models.DateTimeField(blank = False)
    end_date = models.DateTimeField(blank = False)
    total_cost = models.FloatField(blank = False)
    is_two_wheeler = models.BooleanField(default = False)
    alphanumeric_string = models.CharField(max_length = 100, blank = False, unique = True)
    is_active = models.BooleanField(default = True)

    class Meta:
        db_table = 'Bookings'


class Discount(models.Model):

    # id added automatically
    discount_type = models.CharField(max_length = 30, blank = False, default = '')
    discount_percent = models.IntegerField()

    class Meta:
        db_table = 'Discounts'
