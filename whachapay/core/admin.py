from django.contrib import admin
from core.models import (Deal, Dealer, IPAddress, Make, MakeYear, Model,
                         ModelYear, Trim, TrimYear, User, UserIP, Vehicle)

admin.site.register(Deal)
admin.site.register(Dealer)
admin.site.register(IPAddress)
admin.site.register(Make)
admin.site.register(MakeYear)
admin.site.register(Model)
admin.site.register(ModelYear)
admin.site.register(Trim)
admin.site.register(TrimYear)
admin.site.register(User)
admin.site.register(UserIP)
admin.site.register(Vehicle)
