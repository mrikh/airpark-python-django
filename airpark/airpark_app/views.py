from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password
from datetime import datetime

from rest_framework.parsers import JSONParser
from .models import *
from .serializers import *
from rest_framework.exceptions import ValidationError
import stripe
import secrets
import math
import pytz

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
def payment_intent(request):
    
    body = JSONParser().parse(request)
    
    customer_id = body['customer_id']
    car_park_id = body['car_park_id']
    email = body['email']
    is_old = body['is_old']
    is_logged_in = body['is_logged_in']
    car_wash = body['car_wash']
    end_date = body['end_date']
    start_date = body['start_date']
    is_handicap = body['is_handicap']

    result = __calclulate_price(end_date, start_date, car_park_id, is_old, is_handicap, is_logged_in, email, car_wash)
    
    intent = stripe.PaymentIntent.create(
        #multiply by 100 as everything is in cents
        amount=result[0] * 100,
        currency='eur',
        customer=customer_id,
    )

    client_secret = intent.client_secret   
    return JsonResponse({"code" : 200, 'data': {'client_secret' : client_secret}, 'message' : 'Success'})

@api_view(['POST'])
def payment_done(request):

    body = JSONParser().parse(request)
    
    car_park_id = body['car_park_id']
    email = body['email']
    is_old = body['is_old']
    is_logged_in = body['is_logged_in']
    car_wash = body['car_wash']
    end_date = body['end_date']
    start_date = body['start_date']
    is_handicap = body['is_handicap']
    is_two_wheeler = body['is_two_wheeler']

    result = __calclulate_price(end_date, start_date, car_park_id, is_old, is_handicap, is_logged_in, email, car_wash)

    body['car_park'] = car_park_id
    body['start_date'] = datetime.fromtimestamp(body['start_date']/1000, tz=pytz.utc)
    body['end_date'] = datetime.fromtimestamp(body['end_date']/1000, tz=pytz.utc)
    body['total_cost'] = result[0]
    body['alphanumeric_string'] = secrets.token_hex(16)

    try:
        booking_serializer = BookingSerializer(data=body)
        if booking_serializer.is_valid(raise_exception = True):
            booking = booking_serializer.save()
            data = booking_serializer.data

            #successfully saved so now we update counts in the carparks
            carpark = CarPark.objects.get(id=booking.car_park.id)
            if booking.is_handicap:
                carpark.dis_capacity -= 1
            elif booking.is_two_wheeler:
                carpark.tw_capacity -= 1
            else:
                carpark.normal_capacity -= 1
            carpark.save()
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


@api_view(['GET'])
def airports_list(request):

    car_parks = CarPark.objects.all()
    airports = {}
    for j in car_parks:
        if j.airport_id not in airports:
            airports[j.airport_id] = j.airport_name
    listofDicts = []
    for key, value in airports.items():
        dictionary = {"airport_id": key, "airport_name": value}
        listofDicts.append(dictionary)
    jsonData = {"airports": listofDicts}
    return JsonResponse({"code": 200, "data": jsonData})


@api_view(['GET'])
def get_availability(request):

    body = request.query_params
    airport_id = body.get('airport_id', None)
    start_date = int(body.get('start_date', None))
    end_date = int(body.get('end_date', None))
    is_handicap = body.get('is_handicap', None)
    is_two_wheeler = body.get('is_two_wheeler', None)

    # filter out the car parks not in the selected airport
    car_parks = CarPark.objects.all().filter(airport_id=airport_id)

    # filter out car parks that don't have handicap/two wheeler spots if applicable
    if is_handicap == 1:
        car_parks = car_parks.filter(dis_capacity__gte = 1)
    elif is_two_wheeler == 1:
        car_parks = car_parks.filter(tw_capacity__gte = 1)
    else:
        car_parks = car_parks.filter(normal_capacity__gte = 1)

    if len(car_parks) == 0:
        return JsonResponse({"code": 404, "data": None, "message" : "Data not Found"})

    # ensure there is space available by checking the other bookings
    # this method may underestimate the amount of free spaces sometimes but it's simple

    # filter in bookings that would overlap with the customer's booking
    # bookings = Booking.objects.filter(Booking.booking_start_date < pEnd_date_timestamp and Booking.booking_end_date >
    #                                   pStart_date_timestamp)

    # filter out bookings that are not for car parks in this airport
    # for i in range(bookings):
    #     bookings = bookings.filter(bookings[i].car_park_id in car_parks)

    # make a dict of each car park in the airport and the number of free spaces
    # suitable_car_parks = {"car_park": "spaces"}
    # most_suitable = 0
    # spaces = 0
    # car_park_bookings = bookings
    # for j in range(car_parks):
    #    for k in range(bookings):
    #        car_park_bookings = bookings.filter(bookings[k].car_park_id == car_parks[j].car_park_id)
    #    bookings_count = car_park_bookings.count()
    #    if car_parks[j].max_capacity - bookings_count > 0:
    #        spaces = car_parks[j].max_capacity - bookings_count
    #        suitable_car_parks[car_parks[j]] = spaces
    #        if spaces > most_suitable:
    #            most_suitable = spaces

    # select best match and other match based on available spaces
#    for key, value in suitable_car_parks.items():
#        if spaces == value:
#            best_match = key
#        else:
#            return JsonResponse({"code": 400, 'message': 'There are no available spaces at your selected airport'})

    #only show long term if atleast 24 hours.
    difference_seconds = (end_date - start_date)/1000
    difference = max(difference_seconds/3600, 1)
    difference = difference/24

    #move long term if difference > 1 to top
    removeFromPos = -1
    for i in range(len(car_parks)):
        park = car_parks[i]

        if difference >= 1:
            if park.is_long_term:
                removeFromPos = i
                break
        else:
            if not park.is_long_term:
                removeFromPos = i
                break
                
    
    best_match_json = CarPark()
    #some value was found and removed
    if removeFromPos > -1:
        best_match_json = CarParkSerializer(car_parks[removeFromPos]).data
    else:
        best_match_json = car_parks[0].data

    car_parks = car_parks.filter().exclude(id = best_match_json['id'])

    # if len(car_parks) > 1:
        # for value in suitable_car_parks.values():
        #     if match_value < value < spaces:
        #         match_value = value
        # for key, value in suitable_car_parks.items():
        #     if spaces == value:
        #         other_match = key
    
    jsonData = {"best_match": best_match_json, "other_matches": CarParkSerializer(car_parks, many=True).data}
    return JsonResponse({"code": 200, "data": jsonData})


@api_view(['POST'])
def calc_price(request):

    body = JSONParser().parse(request)
    try:
        car_park_id = body['car_park_id']
        customer_name = body['customer_name']
        email = body['email']
        phone = body['phone']
        car_reg = body['car_reg']
        is_old = body['is_old']
        is_logged_in = body['is_logged_in']
        car_wash = body['car_wash']
        end_date = body['end_date']
        start_date = body['start_date']
        is_handicap = body['is_handicap']
        version = body['version']
        is_two_wheeler = body['is_two_wheeler']

        result = __calclulate_price(end_date, start_date, car_park_id, is_old, is_handicap, is_logged_in, email, car_wash)      

        customer = stripe.Customer.create(email = email)
        key = stripe.EphemeralKey.create(customer=customer, stripe_version=version)
    
        return JsonResponse({"code" : 200, 'data': {'key' : key, 'total' : result[0], 'discounts' : result[1]}, 'message' : 'Success'})
    except Exception:
        return JsonResponse({"code" : 400, 'message' : 'Something went wrong'})

    return JsonResponse({"code" : 400, 'message' : 'Something went wrong'})

def __calclulate_price(end_date, start_date, carpark_id, is_old, is_handicap, is_logged_in, email, car_wash):
    
    #convert to seconds and then to hours. Atleast 1 hour is the slot
    difference_seconds = (end_date - start_date)/1000
    difference = max(difference_seconds/3600, 1)
    
    carpark = CarPark.objects.get(id = carpark_id)

    if carpark.is_long_term == True:
        #round up the day
        difference = math.ceil(difference/24)

    calculated_price = carpark.price * difference
    
    if car_wash:
        calculated_price += 25

    total_discount = 0
    discounts_applied = []

    if is_old:
        discount = Discount.objects.get(discount_type = 'old_age')
        total_discount += discount.discount_percent
        discounts_applied.append('Old Age Discount')

    if is_handicap:
        discount = Discount.objects.get(discount_type = 'disabled')
        total_discount += discount.discount_percent
        discounts_applied.append('Physically Disabled Discount')

    if is_logged_in:
        discount = Discount.objects.get(discount_type = 'login')
        total_discount += discount.discount_percent
        discounts_applied.append('Discount for being a registered user.')

    #get current user bookings
    try:
        if len(Booking.objects.all().filter(email = email)) > 5:
            discount = Discount.objects.get(discount_type = 'frequent_user')
            total_discount += discount.discount_percent
            discounts_applied.append('Discount for being a frequent app user.')
    except Exception as e:
        #do nothing. Exception raised if no booking exists etc.
        print(e)

    #atleast 30% discount
    total_discount = min(30, total_discount)
    final_price = calculated_price - (total_discount/100 * calculated_price)
    return (math.ceil(final_price), discounts_applied)


@api_view(['GET'])
def get_upcoming_bookings(request):

    body = request.query_params
    user_id = body.get('user_id', None)

    current_date = datetime.today()
    # retrieve all bookings and filter in the ones that have not ended
    bookings = Booking.objects.all().filter(end_date__gte = current_date)

    booking_list = [""] * 9
    listofDicts = []
    for b in bookings:
        carpark = CarPark.objects.get(id=b.car_park_id)
        booking_list[0] = b.id
        booking_list[1] = carpark.latitude
        booking_list[2] = carpark.longitude
        booking_list[3] = carpark.car_park_name
        booking_list[4] = carpark.airport_name
        booking_list[5] = b.start_date.timestamp()
        booking_list[6] = b.end_date.timestamp()
        booking_list[7] = b.total_cost
        booking_list[8] = carpark.image

        booking_dict = {"booking_id": booking_list[0], "carpark_lat": booking_list[1], "carpark_long": booking_list[2],
                        "carpark_name": booking_list[3], "airport_name": booking_list[4], "start_date": booking_list[5],
                        "end_date": booking_list[6], "total_price": booking_list[7], "carpark_image": booking_list[8], "alphanumeric_string" : b.alphanumeric_string, "is_long_term" : carpark.is_long_term}
        listofDicts.append(booking_dict)
    jsonData = {"upcoming": listofDicts}
    return JsonResponse({"code": 200, "data": jsonData})


@api_view(['GET'])
def get_past_bookings(request):

    body = request.query_params
    user_id = body.get('user_id', None)

    current_date = datetime.today()
    # retrieve all bookings and filter in the ones that have not ended
    bookings = Booking.objects.all().filter(end_date__lte = current_date)

    booking_list = [""] * 9
    listofDicts = []
    for b in bookings:
        carpark = CarPark.objects.get(id=b.car_park_id)
        booking_list[0] = b.id
        booking_list[1] = carpark.latitude
        booking_list[2] = carpark.longitude
        booking_list[3] = carpark.car_park_name
        booking_list[4] = carpark.airport_name
        booking_list[5] = b.start_date.timestamp()
        booking_list[6] = b.end_date.timestamp()
        booking_list[7] = b.total_cost
        booking_list[8] = carpark.image

        booking_dict = {"booking_id": booking_list[0], "carpark_lat": booking_list[1], "carpark_long": booking_list[2],
                        "carpark_name": booking_list[3], "airport_name": booking_list[4], "start_date": booking_list[5],
                        "end_date": booking_list[6], "total_price": booking_list[7], "carpark_image": booking_list[8], "alphanumeric_string" : b.alphanumeric_string, "is_long_term" : carpark.is_long_term}
        listofDicts.append(booking_dict)
#       return JsonResponse({"code": 400, "message": "You have no previous bookings"})
    jsonData = {"history": listofDicts}
    return JsonResponse({"code": 200, "data": jsonData})


@api_view(['PUT'])
def cancel_booking(request):

    body = request.query_params
    booking_id = body.get('booking_id', None)
    booking = Booking.objects.get(id=booking_id)
    booking.is_active = 0
    booking.save()

    utc = pytz.UTC
    current_date = datetime.today().replace(tzinfo=utc)
    end_date = booking.end_date.replace(tzinfo=utc)
    if end_date > current_date:
        end_date = current_date

    return JsonResponse({"code": 200})