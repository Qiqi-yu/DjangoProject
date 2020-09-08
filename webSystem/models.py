from django.db import models
from enum import Enum
# Create your models here.


from django.contrib.auth.models import AbstractUser


class SystemUser(AbstractUser):
    # 对User属性的判断
    is_student = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    # 权限在接口处通过对User属性判断即可


