from django.contrib import admin
from .models import producty,Contact,Order,orderupdate

# Register your models here.

admin.site.register(producty)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(orderupdate)