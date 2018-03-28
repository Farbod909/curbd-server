from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_safe

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


@require_POST
def make_reservation(request):
    pass


@require_safe
def add_host_view(request):
    return render(request, 'parking/add_host.html')
