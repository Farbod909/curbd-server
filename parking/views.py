from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods, require_safe
from django.core import serializers
from django.http import JsonResponse
from django.conf import settings

import json
import pytz
import dateutil.parser
from math import acos, sin, cos

from .models import ParkingSpace


@require_safe
def get_available_parking_spaces(request):
    latitude = request.GET.get('lat')
    longitude = request.GET.get('long')
    radius = request.GET.get('radius')  # radius in miles
    start_datetime_iso = request.GET.get('start')
    end_datetime_iso = request.GET.get('end')


    pst = pytz.timezone('US/Pacific')
    # TODO: MAKE TIMEZONE WORK EVERYWHERE!!!

    start_datetime = pst.localize(dateutil.parser.parse(start_datetime_iso))
    end_datetime = pst.localize(dateutil.parser.parse(end_datetime_iso))

    # TODO: fix accuracy of radius search
    locations_within_radius = ParkingSpace.objects.raw(
        'SELECT * FROM parking_parkingspace space '
        'WHERE ('
        '           acos(1 - abs((sin(space.latitude * 0.0175) * sin(%(input_lat)s * 0.0175) '
        '               + cos(space.latitude * 0.0175) * cos(%(input_lat)s * 0.0175) * '
        '                 cos((%(input_long)s * 0.0175) - (space.longitude * 0.0175)) '
        '              ) - 1)) * 3959 <= %(input_radius)s'
        '      )',
        {
            'input_lat': latitude,
            'input_long': longitude,
            'input_radius': radius,
        }
    )

    # print("**********************")
    # for space in locations_within_radius:
    #     a = sin(float(space.latitude) * 0.0175) * sin(34.063324 * 0.0175)
    #     b = cos(float(space.latitude) * 0.0175) * cos(34.063324 * 0.0175)
    #     c = cos((-118.392217 * 0.0175) - (float(space.longitude) * 0.0175))
    #
    #     print(a)
    #     # print(
    #     #     acos(
    #     #         sin(float(space.latitude) * 0.0175) * sin(34.063324 * 0.0175)
    #     #         +
    #     #         cos(float(space.latitude) * 0.0175) * cos(34.063324 * 0.0175) * cos((-118.392217 * 0.0175) - (float(space.longitude) * 0.0175))
    #     #     ) * 3959
    #     # )
    # print("**********************")

    # TODO: check 'available_spaces' field against reservations to get availability

    available_locations = []
    for location in locations_within_radius:
        unreserved_spaces = location.unreserved_spaces(start_datetime, end_datetime)
        if unreserved_spaces > 0:
            location_dict = location.__dict__
            del location_dict['_state']
            location_dict['latitude'] = float(location_dict['latitude'])
            location_dict['longitude'] = float(location_dict['longitude'])
            location_dict['unreserved_spaces'] = unreserved_spaces
            available_locations.append(location_dict)

    return HttpResponse(json.dumps(available_locations), content_type='application/json')