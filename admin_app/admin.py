from django.contrib import admin

from .models import Admin, AdminAdress, AdminDoc

# Register your models here.

admin.site.register(Admin)
admin.site.register(AdminDoc)
admin.site.register(AdminAdress)
