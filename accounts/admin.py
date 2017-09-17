from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, Host, Customer, Car

# Register your models here.
admin.site.register(User)
admin.site.register(Host)
admin.site.register(Customer)
admin.site.register(Car)
admin.site.unregister(Group)