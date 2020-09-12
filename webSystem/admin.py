from django.contrib import admin
from .models import SystemUser, Equipment, LoanApplication,SystemLog,Mail
# Register your models here.

admin.site.register(SystemUser)
admin.site.register(Equipment)
admin.site.register(LoanApplication)
admin.site.register(SystemLog)
admin.site.register(Mail)