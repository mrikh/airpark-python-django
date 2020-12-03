from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password

from rest_framework.parsers import JSONParser
from .models import *
from .serializers import *
from rest_framework.exceptions import ValidationError
import stripe

stripe.api_key = 'sk_test_51HrvFLISFKjjBkELcTQH2DsC0vWYvqv4bA3MEZD0q7u8QIFzlqlJJ9SGqtSeUMDGIFubl7unKkVaR6luhKLsZejs00wY4PIg3h'


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
def ephemeral_key(request):

    body = JSONParser().parse(request)
    email = body['email']
    version = body['api_version']

    customer = stripe.Customer.create(email = email)
    key = stripe.EphemeralKey.create(customer=customer, stripe_version=version)
    return JsonResponse({"code" : 200, 'data': key, 'message' : 'Success'})


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


@api_view(['GET'])
def get_airports(request):

    car_parks = CarPark.objects.all()
    for i in range(car_parks):
        jsonData = {"airports": {"airport_id": car_parks[i].airport_id, "airport_name": car_parks[i].airport_name}}
    return JsonResponse({"code": 200, "data": jsonData})


@api_view(['GET'])
def get_availability(pAirport_id, pStart_date_timestamp, pEnd_date_timestamp, pHandicap_spot, pIs_two_wheeler):

    # filter out the car parks not in the selected airport
    car_parks = CarPark.objects.all().filter(Airport_id=pAirport_id)

    # filter out car parks that don't have handicap/two wheeler spots if applicable
    if pHandicap_spot == 1:
        car_parks = car_parks.filter(CarPark.max_dis_capacity >= 1)
    if pIs_two_wheeler == 1:
        car_parks = car_parks.filter(CarPark.max_tw_capacity >= 1)

    # ensure there is space available by checking the other bookings
    # this method may underestimate the amount of free spaces sometimes but it's simple

    # filter in bookings that would overlap with the customer's booking
    bookings = Booking.objects.filter(Booking.booking_start_date < pEnd_date_timestamp and Booking.booking_end_date >
                                      pStart_date_timestamp)

    # filter out bookings that are not for car parks in this airport
    for i in range(bookings):
        bookings = bookings.filter(bookings[i].car_park_id in car_parks)

    # make a dict of each car park in the airport and the number of free spaces
    suitable_car_parks = {"car_park": "spaces"}
    most_suitable = 0
    spaces = 0
    car_park_bookings = bookings
    for j in range(car_parks):
        for k in range(bookings):
            car_park_bookings = bookings.filter(bookings[k].car_park_id == car_parks[j].car_park_id)
        bookings_count = car_park_bookings.count()
        if car_parks[j].max_capacity - bookings_count > 0:
            spaces = car_parks[j].max_capacity - bookings_count
            suitable_car_parks[car_parks[j]] = spaces
            if spaces > most_suitable:
                most_suitable = spaces

    # select best match and other match based on available spaces
    for key, value in suitable_car_parks.items():
        if spaces == value:
            best_match = key
        else:
            return JsonResponse({"code": 400, 'message': 'There are no available spaces at your selected airport'})

    match_value = 0
    if len(suitable_car_parks) > 1:
        for value in suitable_car_parks.values():
            if match_value < value < spaces:
                match_value = value
        for key, value in suitable_car_parks.items():
            if spaces == value:
                other_match = key
        jsonData = {"best_match": {"carpark_id": best_match.car_park_id, "carpark_name": best_match.carpark_name,
                                   "carpark_rate": best_match.carpark_rate, "is_long_term": best_match.is_long_term,
                                   "carpark_image": best_match.carpark_image, "carpark_lat": best_match.carpark_lat,
                                   "carpark_long": best_match.carpark_long}, "other_matches": [{"carpark_id":
                                   other_match.car_park_id, "carpark_name": other_match.carpark_name, "carpark_rate":
                                   other_match.carpark_rate, "is_long_term": other_match.is_long_term, "carpark_image":
                                   other_match.carpark_image, "carpark_lat": other_match.carpark_lat, "carpark_long":
                                   other_match.carpark_long}]}

        return JsonResponse({"code": 200, "data": jsonData})
    elif len(suitable_car_parks) == 1:
        jsonData = {"best_match": {"carpark_id": best_match.car_park_id, "carpark_name": best_match.carpark_name,
                                   "carpark_rate": best_match.carpark_rate, "is_long_term": best_match.is_long_term,
                                   "carpark_image": best_match.carpark_image, "carpark_lat": best_match.carpark_lat,
                                   "carpark_long": best_match.carpark_long}}
        return JsonResponse({"code": 200, "data": jsonData})
    elif len(suitable_car_parks) < 1:
        return JsonResponse({"code": 400, 'message': 'There are no available spaces at your selected airport'})


@api_view(['POST'])
def post_price(pcar_park_id, pname, pemail, pphone, pcar_reg, pis_old, pis_logged_in):

    car_park = CarPark.objects.all().filter(car_park_id=pcar_park_id)
    price = car_park.price
#    if pis_old == 1
#        price = price

