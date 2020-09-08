from django.db import models
from enum import Enum
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# 判断用户从is_student到is_provider的状态转换
class ExamStatus(Enum):
    # 未提交申请
    NORMAL = 1
    # 提交审核中
    EXAMING = 2
    # 被拒绝
    REJECT = 3


class SystemUser(AbstractUser):
    # 对User属性的判断
    is_student = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    examining = models.BooleanField(default=False)
    # 暂时加入对登录状态的判断
    logged = models.BooleanField(default=False)
    # 用户提交审核申请的状态判断
    examining_status = models.PositiveSmallIntegerField(default=ExamStatus.NORMAL)

    # 当用户提交审核申请时候 需要的信息
    # 实验室信息
    info_lab = models.CharField(max_length=50, default='')
    # 地址
    info_address = models.CharField(max_length=50, default='')
    # 联系电话
    info_tel = models.CharField(max_length=20, default='')
    # 设备简单描述
    info_description = models.TextField(max_length=200, default='')

    # TODO:权限在接口处通过对User属性判断即可


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


class Equipment(models.Model):
    status = models.PositiveSmallIntegerField(default=EquipmentStatus.EXIST)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="owner")
    borrower = models.ForeignKey('SystemUser', on_delete=models.SET_DEFAULT, default='', related_name="borrower")
    loan_end_time = models.DateTimeField(default=timezone.now)


class ApplicationStatus(Enum):
    # 发出待审核
    SENTED = 1
    # 正在进行
    ON_PROCESS = 2
    # 未通过审核
    NOT_PASS = 3
    # 租期结束
    RENT_END = 4


class LoanApplication(models.Model):
    status = models.PositiveSmallIntegerField(default=ApplicationStatus.SENTED)
    loaner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="loaner")
    applicant = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="applicant")
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    loan_start_time = models.DateTimeField(default=timezone.now)
    loan_end_time = models.DateTimeField(default=timezone.now)
