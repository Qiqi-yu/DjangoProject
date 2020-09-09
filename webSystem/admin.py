from django.contrib import admin
from .models import SystemUser, Equipment, LoanApplication
# Register your models here.

admin.site.register(SystemUser)
admin.site.register(Equipment)
admin.site.register(LoanApplication)
