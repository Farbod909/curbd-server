from rest_framework.pagination import CursorPagination


class PreviousReservationsCursorPagination(CursorPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    ordering = '-start_datetime'  # '-creation' is default
