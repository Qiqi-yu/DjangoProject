from django.db import models
from enum import Enum
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# 判断用户从is_student到is_provider的状态转换

class SystemUser(AbstractUser):

    # 用户的属性 student, provider, admin
    role = models.CharField(max_length=20, default='student')
    # 用户提交审核申请的状态判断 Normal Examining Reject Pass
    examining_status = models.CharField(max_length=20, default='Normal')

    # 当用户提交审核申请时候 需要的信息
    # 实验室信息
    info_lab = models.CharField(max_length=50, default='')
    # 地址
    info_address = models.CharField(max_length=50, default='')
    # 联系电话
    info_tel = models.CharField(max_length=20, default='')
    # 设备简单描述
    info_description = models.TextField(max_length=200, default='')

    # 审核被拒绝时的理由
    info_reject=models.TextField(max_length=200,default='')

    def has_student_privileges(self):
        return self.role in {'student', 'provider'}

    def has_provider_privileges(self):
        return self.role == 'provider'

    def has_admin_privileges(self):
        return self.role == 'admin'


class Equipment(models.Model):
    # EquipmentStatus = (
    #     (1, 'exist'), # 已添加
    #     (2, 'wait_on_shelf'), # 等待批准上架
    #     (3, 'on_shelf'), # 已上架
    #     (4, 'wait_on_loan'), # 等待批准借出
    #     (5, 'on_loan'), # 已借出
    # )
    status = models.CharField(max_length=20, default='exist')
    name = models.CharField(max_length=100, default='')
    owner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="owner")
    info = models.TextField(max_length=1000, default='')
    # unnecessary
    # borrower = models.ForeignKey('SystemUser', on_delete=models.SET_DEFAULT, default='', related_name="borrower")
    # unnecessary
    # loan_end_time = models.DateTimeField(default=timezone.now)


class LoanApplication(models.Model):
    # ApplicationStatus = (
    #     (0, 'pending'),   # 已发出，等待审核
    #     (1, 'approved'),  # 通过
    #     (2, 'rejected'),  # 拒绝
    # )
    status = models.CharField(max_length=20, default='pending')
    applicant = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="applicant")
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    statement = models.CharField(max_length=1000, default='')
