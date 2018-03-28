from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^add_host/', views.add_host_view, name='add_host'),
    url(r'^nearby_spaces/', views.get_available_parking_spaces),
]
