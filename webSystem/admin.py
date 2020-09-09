from django.contrib import admin
from .models import SystemUser
from .models import Equipment
from .models import LoanApplication
# Register your models here.

admin.site.register(SystemUser)
admin.site.register(Equipment)
admin.site.register(LoanApplication)
