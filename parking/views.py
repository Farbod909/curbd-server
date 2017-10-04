from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods, require_safe
from django.core import serializers
from django.http import JsonResponse


from .models import ParkingSpace


@require_safe
def get_available_parking_spaces(request):
    latitude = request.GET.get('lat')
    longitude = request.GET.get('long')
    radius = request.GET.get('radius')  # radius in miles

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

    # TODO: check 'available_spaces' field against reservations to get availability

    json_obj = serializers.serialize('json', locations_within_radius)
    return HttpResponse(json_obj, content_type='application/json')