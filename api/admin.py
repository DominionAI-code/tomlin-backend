from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, MenuItem, Inventory, Employee, LeasePayment

admin.site.register(CustomUser)
admin.site.register(MenuItem)
admin.site.register(Inventory)
admin.site.register(Employee)
admin.site.register(LeasePayment)
