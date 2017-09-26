from django.shortcuts import render
from django.http import HttpResponse

from .models import ParkingSpace


def get_available_parking_spaces(request):
    latitude = request.GET.get('lat')
    longitude = request.GET.get('long')
    radius = request.GET.get('radius')

    # TODO: fix accuracy of radius search
    locations_within_radius = ParkingSpace.objects.raw(
        'SELECT * FROM parking_parkingspace space '
        'WHERE ('
        '           acos(sin(space.latitude * 0.0175) * sin(%(input_lat)s * 0.0175) '
        '               + cos(space.latitude * 0.0175) * cos(%(input_lat)s * 0.0175) * '
        '                 cos((%(input_long)s * 0.0175) - (space.longitude * 0.0175)) '
        '              ) * 3959 <= %(input_radius)s'
        '      )',
        {
            'input_lat': latitude,
            'input_long': longitude,
            'input_radius': radius,
        }
    )

    return HttpResponse(locations_within_radius)