from django.db import models
from enum import Enum
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class SystemUser(AbstractUser):
    verif_code = models.CharField(max_length=32, default='')

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
    info_reject = models.TextField(max_length=200, default='')

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
    # )
    status = models.CharField(max_length=20, default='exist')
    name = models.CharField(max_length=100, default='')
    owner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="owner")

    # 设备的简单介绍
    info = models.TextField(max_length=1000, default='')

    # 用户提交审核申请的状态判断 Normal Examining Reject Pass
    examining_status = models.CharField(max_length=20, default='Normal')

    # 审核被拒绝时的理由
    info_reject = models.TextField(max_length=200, default='')


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
    response = models.CharField(max_length=1000, default='')


# 系统日志
class SystemLog(models.Model):
    # 类型
    type = models.CharField(max_length=50, default='')
    # 发出者
    sender = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="sender")
    # 发出时间
    send_time = models.DateTimeField(default=timezone.now)
    # 详细信息
    detail = models.TextField(max_length=1000, default='')


# 站内信
class Mail(models.Model):
    # 发出者
    sender = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="sender")
    # 接受者
    receiver = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="receiver")
    # 发出时间
    send_time = models.DateTimeField(default=timezone.now)
    # 详细信息
    detail = models.TextField(max_length=1000, default='')
    # 读取状态
    read = models.BooleanField(default=False)
