from django.db import models
from enum import Enum
# Create your models here.
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


# 判断用户从is_student到is_provider的状态转换

class SystemUser(AbstractUser):

    # 用户的属性 student, provider, admin
    role = models.CharField(max_length=20, default='student')
    # 暂时加入对登录状态的判断
    logged = models.BooleanField(default=False)
    # 用户提交审核申请的状态判断 Normal Examining Reject
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
        return self.role is 'provider'

    def has_admin_privileges(self):
        return self.role is 'admin'


class Equipment(models.Model):
    # EquipmentStatus = (
    #     (1, 'exist'), # 已添加
    #     (2, 'wait_on_shelf'), # 等待批准上架
    #     (3, 'on_shelf'), # 已上架
    #     (4, 'wait_on_loan'), # 等待批准借出
    #     (5, 'on_loan'), # 已借出
    # )
    status = models.CharField(max_length=20, default='exist')
    name = models.CharField(max_length=100)
    owner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="owner")
    # unnecessary
    borrower = models.ForeignKey('SystemUser', on_delete=models.SET_DEFAULT, default='', related_name="borrower")
    # unnecessary
    loan_end_time = models.DateTimeField(default=timezone.now)

    # 上架信息 info


class LoanApplication(models.Model):
    # ApplicationStatus = (
    #     (1, 'sented'), # 发出待审核
    #     (2, 'on_process'), # 正在进行
    #     (3, 'not_pass'), # 未通过审核
    #     (4, 'rent_end'), # 租期结束
    # )

    # sent
    # approved
    # disapproved

    status = models.CharField(max_length=20, default='sented')
    loaner = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="loaner")
    applicant = models.ForeignKey('SystemUser', on_delete=models.CASCADE, related_name="applicant")
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    loan_start_time = models.DateTimeField(default=timezone.now)
    loan_end_time = models.DateTimeField(default=timezone.now)
