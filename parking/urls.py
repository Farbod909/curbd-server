from django.urls import path

from . import views


urlpatterns = [
    path('add_host/', views.add_host_view, name='add_host'),
]
