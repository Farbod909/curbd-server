from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'customers': reverse('customer-list', request=request, format=format),
        'hosts': reverse('host-list', request=request, format=format),
        'cars': reverse('car-list', request=request, format=format),
        'parkingspaces': reverse('parkingspace-list', request=request, format=format),
        'fixedavailabilities': reverse('fixedavailability-list', request=request, format=format),
        'repeatingavailabilities': reverse('repeatingavailability-list', request=request, format=format),
        'reservations': reverse('reservation-list', request=request, format=format),

    })
