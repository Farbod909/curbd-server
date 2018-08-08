from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('parking/', include('parking.urls')),
]
