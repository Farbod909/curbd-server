from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from .views import apple_app_site_association_view


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # This was moved to the curbdparking.com domain.
    # We might need to move it back here in the future under the curbd.app domain?
    # path('apple-app-site-association/', apple_app_site_association_view, name='apple-app-site-association'),
    path('parking/', include('parking.urls')),
]
