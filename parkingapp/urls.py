from django.conf.urls import url, include
from django.contrib import admin

from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^api/', include('api.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^parking/', include('parking.urls')),
]
