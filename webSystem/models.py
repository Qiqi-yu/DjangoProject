from django.db import models
from enum import Enum
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class EquipmentStatus(Enum):
    # 已添加
    EXIST = 1
    # 等待批准上架
    WAIT_ON_SHELF = 2
    # 已上架
    ON_SHELF = 3
    # 等待批准借出
    WAIT_ON_LOAN = 4
    # 已借出
    ON_LOAN = 5


class SystemUser(AbstractUser):
    # 对User属性的判断
    is_student = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    # 暂时加入对登录状态的判断
    logged = models.BooleanField(default=False)

    # 权限在接口处通过对User属性判断即可


class ApplicationStatus(Enum):
    # 发出待审核
    SENTED=1
    # 正在进行
    ON_PROCESS=2
    # 未通过审核
    NOT_PASS=3
    # 租期结束
    RENT_END=4


class Equipment(models.Model):
    status = models.PositiveSmallIntegerField(default=EquipmentStatus.EXIST)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="owner")
    borrower = models.ForeignKey('SystemUser', on_delete=models.SET_DEFAULT, default='', related_name="borrower")
    loan_end_time = models.DateTimeField(default=timezone.now)


class LoanApplication(models.Model):
    status = models.PositiveSmallIntegerField(default=ApplicationStatus.SENTED)
    loaner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="loaner")
    applicant = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="applicant")
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    loan_start_time = models.DateTimeField(default=timezone.now)
    loan_end_time = models.DateTimeField(default=timezone.now)