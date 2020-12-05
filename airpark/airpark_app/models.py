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

    # id added automatically for booking

    # id of car park associated with the booking
    car_park_id = models.ForeignKey(CarPark, on_delete=models.CASCADE)
    user_email = models.CharField(max_length = 50, blank = False, default = '', validators = [validate_email], unique = True)

    booking_start_date = models.DateTimeField()
    booking_end_date = models.DateTimeField()

    total_cost = models.FloatField()

    # duration 0 = short term, 1 = long term
    duration_type = models.IntegerField()

    alphanumeric_string = models.CharField(max_length = 100, blank = False)

    class Meta:
        db_table = 'Bookings'

class Discount(models.Model):

    # id added automatically
    discount_type = models.CharField(max_length = 30, blank = False, default = '')
    discount_percent = models.IntegerField()

    class Meta:
        db_table = 'Discounts'
