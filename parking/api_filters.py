import dateutil.parser
from django.db.models.query import Q
from rest_framework import filters
from rest_framework.exceptions import ValidationError


class LocationAndTimeAvailableFilter(filters.BaseFilterBackend):
    """
    Filter the returned parking spaces to a given location and time
    """

    def filter_queryset(self, request, queryset, view):
        bottom_left_lat = request.query_params.get('bl_lat', None)
        bottom_left_long = request.query_params.get('bl_long', None)
        top_right_lat = request.query_params.get('tr_lat', None)
        top_right_long = request.query_params.get('tr_long', None)
        start_datetime_iso = request.query_params.get('start', None)
        end_datetime_iso = request.query_params.get('end', None)

        location_params = [
            bottom_left_lat, bottom_left_long,
            top_right_lat, top_right_long,
        ]
        time_params = [start_datetime_iso, end_datetime_iso]

        if not any([item is None for item in location_params]):
            # limit queryset to parking spaces within a coordinate box
            queryset = queryset.filter(
                Q(longitude__gte=bottom_left_long),
                Q(longitude__lte=top_right_long),
                Q(latitude__gte=bottom_left_lat),
                Q(latitude__lte=top_right_lat))

        if not any([item is None for item in time_params]):

            start_datetime = dateutil.parser.parse(start_datetime_iso)
            end_datetime = dateutil.parser.parse(end_datetime_iso)

            if start_datetime.tzinfo is None or end_datetime.tzinfo is None:
                raise ValidationError("Timezone must be provided")

            if start_datetime >= end_datetime:
                raise ValidationError("end must be a later date than start")

            # limit queryset to parking spaces with
            # vacant spots in the specified datetime range.
            queryset = [parkingspace for parkingspace in queryset
                        if parkingspace.unreserved_spaces(start_datetime, end_datetime) > 0]

        return queryset


class MinVehicleSizeFilter(filters.BaseFilterBackend):
    """
    Filter the returned parking spaces by minimum vehicle size
    """

    def filter_queryset(self, request, queryset, view):
        min_vehicle_size = request.query_params.get('size', None)

        if min_vehicle_size is not None:
            queryset = queryset.filter(size__gte=min_vehicle_size)

        return queryset
