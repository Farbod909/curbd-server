from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^nearby_spaces/', views.get_available_parking_spaces),
]