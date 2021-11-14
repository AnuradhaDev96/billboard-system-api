from django.contrib import admin
from .models import AReclamborProfileModel, DbProfileModel, LoginProfileModel

# Register your models here.
admin.site.register(AReclamborProfileModel)
admin.site.register(DbProfileModel)
admin.site.register(LoginProfileModel)
