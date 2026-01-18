from django.contrib import admin
from .models import *


class ClientAdmin(admin.ModelAdmin):
    list_per_page = 500

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "code"]

admin.site.register(Client, ClientAdmin)
admin.site.register(Employee)
admin.site.register(Service)
admin.site.register(Incident)
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Infestation)
admin.site.register(Biocide)
admin.site.register(BiocideType)
admin.site.register(BiocideWarning)

