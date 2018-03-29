from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('parking/', include('parking.urls')),
]
