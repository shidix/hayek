from django.contrib import admin
from .models import *


class ClientAdmin(admin.ModelAdmin):
    list_per_page = 500
admin.site.register(Client, ClientAdmin)

admin.site.register(Employee)
admin.site.register(Service)
admin.site.register(Incident)
admin.site.register(ServiceType)
admin.site.register(Infestation)

