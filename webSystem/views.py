from django.shortcuts import render

from .models import SystemUser, Equipment, LoanApplication, SystemLog, Mail
from django.http import HttpResponse
import json
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import redirect
from djangoProject import settings


# Create your views here.


# 注册接口
def logon_request(request):
    # 检验方法
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # 判断参数名是否为空
        if username == '' or password == '' or email == '':
            return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
        # 判断用户名是否已经存在
        elif SystemUser.objects.filter(username=username).exists():
            return HttpResponse(status=400, content=json.dumps({'error': 'user exists'}))
        else:
            user = SystemUser()
            # 先将用户类型设置为普通用户
            user.verif_code = get_random_string(length=32) if settings.VERIFY_EMAIL else ''
            user.role = 'student' if SystemUser.objects.exists() else 'admin'
            user.username = username
            user.set_password(password)
            user.save()
            # 邮件验证
            if settings.VERIFY_EMAIL:
                verif_link = '%s/apis/users/verify/%s/%s' % (settings.FRONTEND_ROOT, username, user.verif_code)
                send_mail(
                    '设备租借平台帐号激活', '',
                    'xuexidepang@yandex.com',
                    [email],
                    html_message='''
                        <p>亲爱的 <strong>%s</strong> 同学你好！</p>
                        <p>请访问 <a href='%s'>这个链接</a> 完成帐号激活。</p>
                        <p>如果链接无效，请直接从 URL 访问 → %s</p>
                    ''' % (username, verif_link, verif_link),
                    fail_silently=False,
                )
            logs_add(user, 'Add', '用户注册')
            return HttpResponse(status=200, content=json.dumps({'user': username}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# 验证邮箱
def user_verify(request, username, code):
    if request.method == 'GET':
        try:
            user = SystemUser.objects.get(username=username)
            if user.verif_code == code:
                user.verif_code = ''
                user.save()
            else:
                raise Exception('Invalid verification code')
        except:
            return HttpResponse(status=400, content=json.dumps({'error': 'Invalid format or verification code'}))
        return redirect('%s/login?verified=%s' % (settings.FRONTEND_ROOT, username))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET'}))


# 登录
def login_request(request):
    # 检验方法
    if request.method == 'POST':
        try:
            # 获取参数
            user_name = request.POST['username']
            password = request.POST['password']
        # 若参数不存在
        except KeyError:
            return HttpResponse(status=400, content=json.dumps({'error': 'no such a user'}))
        else:
            # 若用户名或密码为空
            if user_name == '' or password == '':
                return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
            try:
                # 获取用户信息
                user = SystemUser.objects.get(username=user_name)
                # 检查是否已经通过验证
                if user.verif_code != '':
                    return HttpResponse(status=401, content=json.dumps({'error': 'Please verify e-mail first'}))
                # 验证密码
                if user.check_password(password):
                    # 设置Cookie
                    request.session['username'] = user_name
                    return HttpResponse(status=200, content=json.dumps({'user': user_name, 'role': user.role}))
                else:
                    return HttpResponse(status=400, content=json.dumps({'error': 'password is wrong'}))
            # 若用户不存在
            except SystemUser.DoesNotExist:
                return HttpResponse(status=400, content=json.dumps({'error': 'no such a user'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# 登出
def logout_request(request):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            del request.session['username']
            return HttpResponse(status=200, content=json.dumps({'user': user_name}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# 提供者添加设备
def provider_equipment_add(request):
    # 检验方法
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_provider_privileges():
                name = request.POST.get('name')
                info = request.POST.get('info')
                equipment = Equipment()
                equipment.name = name
                equipment.info = info
                equipment.status = 'exist'
                equipment.owner = user
                equipment.save()
                logs_add(user, 'Add', '添加设备{name}'.format(name=equipment.name))
                return HttpResponse(status=200, content=json.dumps({'id': equipment.id, 'name': name, 'info': info}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# 普通用户申请成为设备提供者
def apply_provider(request):
    if request.method == 'POST':
        try:
            # 获取参数
            lab = request.POST['info_lab']
            address = request.POST['info_address']
            tel = request.POST['info_tel']
            description = request.POST['info_description']
        # 若参数不存在
        except KeyError:
            return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
        else:
            if lab == '' or address == '' or tel == '' or description == '':
                return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
            else:
                if 'username' in request.session:
                    user_name = request.session['username']
                    user = SystemUser.objects.get(username=user_name)

                    # 更新用户的申请信息
                    user.info_lab = lab
                    user.info_address = address
                    user.info_tel = tel
                    user.info_description = description

                    # 更新用户的审核状态
                    user.examining_status = 'Examining'
                    user.save()

                    logs_add(user, 'Change', '申请成为设备提供者')
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# 提供者修改设备
def provider_equipment_update(request, id):
    # 检验方法
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges() or user.has_provider_privileges():
                try:
                    equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
                else:
                    if not user.has_admin_privileges() and equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif not user.has_admin_privileges() and equipment.status != 'exist':
                        return HttpResponse(status=400, content=json.dumps({'error': 'already on shelf'}))
                    else:
                        name = request.POST.get('name')
                        info = request.POST.get('info')
                        equipment.name = name if name else equipment.name
                        equipment.info = info if info else equipment.info
                        equipment.save()
                        logs_add(user, 'Change', '修改设备{name}'.format(name=equipment.name))
                        return HttpResponse(status=200, content=json.dumps(
                            {'id': equipment.id, 'name': equipment.name, 'info': equipment.info}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# 管理查询所有用户
def admin_users_query(request):
    # 检验方法
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges():
                try:
                    examining = request.GET['examining']
                    users_data = []
                    if SystemUser.objects.exists():
                        # 非审核状态下，返回所有数据
                        if examining == 'false':
                            for user in SystemUser.objects.all():
                                users_data.append({'user_name': user.username,
                                                   'user_type': user.role, })
                        # 审核状态下，只返回需要审核的数据
                        elif examining == 'true':
                            query_set = SystemUser.objects.filter(examining_status='Examining')
                            if query_set.exists():
                                for user in query_set.all():
                                    users_data.append({'user_name': user.username,
                                                       'user_type': user.role, 'user_info_lab': user.info_lab,
                                                       'user_info_tel': user.info_tel,
                                                       'user_info_address': user.info_address,
                                                       'user_info_description': user.info_description})
                    return HttpResponse(status=200, content=json.dumps(users_data))
                except KeyError:
                    return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
            else:
                # print(user.role)
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))


# 用户查询自己的信息
def users_info(request):
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 返回json数据
            user_data = {'user_name': user.username,
                         'user_type': user.role, 'user_examining': user.examining_status,
                         'user_info_lab': user.info_lab,
                         'user_info_tel': user.info_tel, 'user_info_address': user.info_address,
                         'user_info_description': user.info_description, 'user_info_reject': user.info_reject}
            return HttpResponse(status=200, content=json.dumps(user_data))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))


# 管理员审核用户申请 用户状态的修改
def admin_check_users_apply(request):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges():
                try:
                    check_username = request.POST['username']
                    check_status = request.POST['pass']
                    # 同意
                    if check_status == 'true':
                        try:
                            apply_user = SystemUser.objects.get(username=check_username)
                            # 将e_s改为Pass 便于通知
                            apply_user.examining_status = 'Pass'
                            apply_user.role = 'provider'
                            apply_user.save()
                            logs_add(user, 'Change', '通过{name}成为提供者的申请'.format(name=apply_user.username))
                            return HttpResponse(status=200)
                        except SystemUser.DoesNotExist:
                            return HttpResponse(status=400, content=json.dumps({'error': 'no such applyed user'}))
                    # 拒绝 需要理由
                    elif check_status == 'false':
                        try:
                            check_reason = request.POST['reason']
                            apply_user = SystemUser.objects.get(username=check_username)
                            # 将e_s改为拒绝 便于通知
                            apply_user.examining_status = 'Reject'
                            apply_user.info_reject = check_reason
                            apply_user.save()
                            logs_add(user, 'Change', '拒绝{name}成为提供者的申请'.format(name=apply_user.username))
                            return HttpResponse(status=200)
                        except KeyError:
                            return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
                except KeyError:
                    return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 用户确认申请审核状态的通知
def users_confirm_apply(request):
    if request.method == 'POST':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 将examining_status恢复默认状态
            user.examining_status = 'Normal'
            user.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 提供者申请上架设备
def provider_equipment_on_shelf(request, id):
    # 检验方法
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges() or user.has_provider_privileges():
                try:
                    equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
                else:
                    if not user.has_admin_privileges() and equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif equipment.status != 'exist':
                        return HttpResponse(status=400, content=json.dumps({'error': 'cannot apply'}))
                    else:
                        equipment.examining_status = 'Examining'
                        equipment.status = 'wait_on_shelf'
                        equipment.save()
                        logs_add(user, 'Change', '申请上架设备{name}'.format(name=equipment.name))
                        return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))

    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 提供者下架设备
def provider_equipment_undercarriage(request, id):
    # 检验方法
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges() or user.has_provider_privileges():
                try:
                    equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
                else:
                    if not user.has_admin_privileges() and equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif equipment.status != 'on_shelf':
                        return HttpResponse(status=400, content=json.dumps({'error': 'cannot apply'}))
                    else:
                        equipment.status = 'exist'
                        equipment.save()
                        logs_add(user, 'Change', '下架设备{name}'.format(name=equipment.name))
                        return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))

    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 管理员审核设备上架申请 设备状态的修改
def admin_check_equipment_apply(request, id):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges():
                try:
                    check_status = request.POST['pass']
                    # 同意
                    if check_status == 'true':
                        try:
                            equipment = Equipment.objects.get(id=id)
                            # 将e_s改为Pass 便于通知
                            equipment.examining_status = 'pass'
                            equipment.status = 'on_shelf'
                            equipment.save()
                            logs_add(user, 'Change', '通过设备{name}上架的申请'.format(name=equipment.name))
                            return HttpResponse(status=200)
                        except Equipment.DoesNotExist:
                            return HttpResponse(status=400, content=json.dumps({'error': 'no such applyed equipment'}))
                    # 拒绝 需要理由
                    elif check_status == 'false':
                        try:
                            check_reason = request.POST['reason']
                            equipment = Equipment.objects.get(id=id)
                            # 将e_s改为拒绝 便于通知
                            equipment.examining_status = 'Reject'
                            equipment.status = 'exist'
                            equipment.info_reject = check_reason
                            equipment.save()
                            logs_add(user, 'Change', '拒绝设备{name}上架的申请'.format(name=equipment.name))
                            return HttpResponse(status=200)
                        except KeyError:
                            return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
                except KeyError:
                    return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 用户确认设备审核状态的通知
def equipment_confirm_apply(request, id):
    if request.method == 'POST':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 将examining_status恢复默认状态
            try:
                equipment = Equipment.objects.get(id=id)
            except:
                return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
            else:
                if equipment.owner != user:
                    return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                elif equipment.examining_status != 'pass' and equipment.examining_status != 'reject':
                    return HttpResponse(status=400, content=json.dumps({'error': 'not comfirm time'}))
                else:
                    equipment.examining_status = 'Normal'
                    equipment.save()
                    return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 简单的删除用户
def admin_users_delete(request, username):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges():
                # try:
                #     delete_user_name = request.POST['username']
                try:
                    delete_user = SystemUser.objects.get(username=username)
                    delete_user.delete()
                    logs_add(user, 'Delete', '删除用户{name}'.format(name=username))
                    return HttpResponse(status=200)
                except SystemUser.DoesNotExist:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no such user'}))
                # except KeyError:
                #     return HttpResponse(status=400,content=json.dumps({'error':'invalid parameters'}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permissions'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 管理员或提供者删除设备
def equipment_delete(request, id):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_admin_privileges() or user.has_provider_privileges():
                try:
                    delete_equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no such equipment'}))
                else:
                    if user.has_provider_privileges() and delete_equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif delete_equipment.status == 'on_shelf' or delete_equipment.status == 'wait_on_shelf':
                        return HttpResponse(status=400, content=json.dumps({'error': 'cannot delete'}))
                    else:
                        delete_equipment.delete()
                        logs_add(user, 'Delete', '删除设备{name}'.format(name=delete_equipment.name))
                        return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permissions'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 一台设备被占用的时间段
def _equipment_occupancies(equipment, after, keep_datetime=False):
    appls = LoanApplication.objects.filter(
        equipment=equipment, status='approved', end_time__gte=after)
    ret = []
    for appl in appls:
        if keep_datetime:
            ret.append([appl.start_time, appl.end_time])
        else:
            ret.append([datetime.timestamp(appl.start_time), datetime.timestamp(appl.end_time)])
    return ret


# 不同角色对所有设备的查询
def equipments_search(request, role):
    # 检验方法
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            username = request.session['username']
            user = SystemUser.objects.get(username=username)
            # 管理员查询所有设备
            if role == 'admin' and user.has_admin_privileges():
                ans = []
                if Equipment.objects.exists():
                    for equipment in Equipment.objects.all():
                        # 获取未来已占用的时间段
                        occs = _equipment_occupancies(equipment, datetime.now())
                        # 记录该设备的各项信息参数
                        equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info,
                                          'status': equipment.status, 'examining_status': equipment.examining_status,
                                          'contact': [equipment.owner.username, equipment.owner.info_lab,
                                                      equipment.owner.info_address,
                                                      equipment.owner.info_tel],
                                          'occupancies': occs}
                        ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            # 提供者查询己方所有设备
            elif role == 'provider' and user.has_provider_privileges():
                equipments = Equipment.objects.filter(owner=user)
                ans = []
                for equipment in equipments:
                    # 获取未来已占用的时间段
                    occs = _equipment_occupancies(equipment, datetime.now())
                    # 记录该设备的各项信息参数
                    equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info,
                                      'status': equipment.status,
                                      'occupancies': occs}
                    ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            # 普通用户或提供者查询所有上架设备
            elif role == 'student' and user.has_student_privileges():
                ans = []
                for equipment in Equipment.objects.filter(status='on_shelf'):
                    # 获取未来已占用的时间段
                    occs = _equipment_occupancies(equipment, datetime.now())
                    # 记录该设备的各项信息参数
                    equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info,
                                      'contact': [equipment.owner.username, equipment.owner.info_lab,
                                                  equipment.owner.info_address,
                                                  equipment.owner.info_tel],
                                      'occupancies': occs}
                    ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permissions'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET'}))


# 通过id获取某台设备的详细信息
def equipment_detail(request, id):
    try:
        equipment = Equipment.objects.get(id=id)
    except:
        return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
    else:
        # 获取未来已占用的时间段
        occs = _equipment_occupancies(equipment, datetime.now())
        return HttpResponse(status=200, content=json.dumps(
            {'id': equipment.id, 'name': equipment.name, 'info': equipment.info, 'status': equipment.status,
             'contact': [equipment.owner.username, equipment.owner.info_lab, equipment.owner.info_address,
                         equipment.owner.info_tel],
             'occupancies': occs}))


def loan_create(request):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            if not user.has_student_privileges():
                return HttpResponse(status=401, content=json.dumps({'error': 'no permission'}))
            try:
                eid = int(request.POST['equipment'])
                start_time = datetime.utcfromtimestamp(int(request.POST['start_time']))
                end_time = datetime.utcfromtimestamp(int(request.POST['end_time']))
                statement = request.POST['statement']
                if start_time >= end_time: raise Exception('Empty timespan')
            except:
                return HttpResponse(status=400, content=json.dumps({'error': 'Incorrect format'}))
            try:
                equipment = Equipment.objects.get(id=eid)
            except SystemUser.DoesNotExist:
                return HttpResponse(status=404, content=json.dumps({'error': 'no such equipment'}))
            # 检查设备是否已上架且未被占用
            if not _equipment_available(equipment, start_time, end_time):
                return HttpResponse(status=400, content=json.dumps({'error': 'Equipment occupied or not on shelf'}))
            appl = LoanApplication()
            appl.applicant = user
            appl.equipment = equipment
            appl.start_time = start_time
            appl.end_time = end_time
            appl.statement = statement
            appl.save()
            logs_add(user, 'Add', '申请租借设备{name}'.format(name=equipment.name))
            return HttpResponse(status=200, content=json.dumps({'id': appl.id}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


def _appl_json_object(appl):
    return {
        'id': appl.id,
        'status': appl.status,
        'owner': {
            'id': appl.equipment.owner.id,
            'username': appl.equipment.owner.username,
        },
        'applicant': {
            'id': appl.applicant.id,
            'username': appl.applicant.username,
        },
        'equipment': {
            'id': appl.equipment.id,
            'name': appl.equipment.name,
            'ownername': appl.equipment.owner.username,
        },
        'start_time': datetime.timestamp(appl.start_time),
        'end_time': datetime.timestamp(appl.end_time),
        'statement': appl.statement,
        'response': appl.response,
    }


# 一台设备是否可以在给定时间段租借
def _equipment_available(equipment, start_time, end_time):
    if equipment.status != 'on_shelf': return False
    occs = _equipment_occupancies(equipment, start_time)
    start_time = datetime.timestamp(start_time)
    end_time = datetime.timestamp(end_time)
    for occ in occs:
        if max(occ[0], start_time) < min(occ[1], end_time): return False
    return True


def loan_my(request):
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            if not user.has_student_privileges():
                return HttpResponse(status=401, content=json.dumps({'error': 'no permission'}))
            # 查找自己发起的所有申请
            appls = list(map(_appl_json_object, LoanApplication.objects.filter(applicant=user)))
            return HttpResponse(status=200, content=json.dumps(appls))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))


def loan_my_equipments(request):
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            if user.has_admin_privileges():
                equipments = Equipment.objects.all()
            elif user.has_provider_privileges():
                equipments = Equipment.objects.filter(owner=user)
            else:
                return HttpResponse(status=401, content=json.dumps({'error': 'no permission'}))
            # 查找自己所有设备对应的所有申请
            appls = []
            for eq in equipments:
                appls += list(map(_appl_json_object, LoanApplication.objects.filter(equipment=eq)))
            if not user.has_admin_privileges():
                appls.sort(key=lambda x: (0 if x['status'] == 'pending' else 1, -x['id']))
            return HttpResponse(status=200, content=json.dumps(appls))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))


def loan_list(request, eid):
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            if not user.has_provider_privileges():
                return HttpResponse(status=401, content=json.dumps({'error': 'no permission'}))
            # 查找设备对应的所有申请
            try:
                equipment = Equipment.objects.get(id=eid)
            except SystemUser.DoesNotExist:
                return HttpResponse(status=404, content=json.dumps({'error': 'no such equipment'}))
            if equipment.owner != user:
                return HttpResponse(status=401, content=json.dumps({'error': 'not its owner'}))
            appls = list(map(_appl_json_object, LoanApplication.objects.filter(equipment=equipment)))
            return HttpResponse(status=200, content=json.dumps(appls))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))


def loan_review(request, id):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            if not user.has_provider_privileges() and not user.has_admin_privileges():
                return HttpResponse(status=401, content=json.dumps({'error': 'no permission'}))
            try:
                appl = LoanApplication.objects.get(id=id)
            except LoanApplication.DoesNotExist:
                return HttpResponse(status=404, content=json.dumps({'error': 'no such application'}))
            if appl.equipment.owner != user and not user.has_admin_privileges():
                return HttpResponse(status=401, content=json.dumps({'error': 'not its owner'}))
            try:
                accept = int(request.POST['accept'])
                response = request.POST['response']
            except:
                return HttpResponse(status=400, content=json.dumps({'error': 'Incorrect format'}))
            if appl.status != 'pending':
                return HttpResponse(status=400, content=json.dumps({'error': 'Already reviewed'}))
            # 检查设备是否已上架且未被占用
            if accept != 0 and not _equipment_available(appl.equipment, appl.start_time, appl.end_time):
                return HttpResponse(status=400, content=json.dumps({'error': 'Equipment occupied or not on shelf'}))
            # 更新申请状态
            appl.status = 'approved' if accept != 0 else 'rejected'
            appl.response = response
            appl.save()
            if appl.status == 'approved':
                logs_add(user, 'Change', '同意用户{username}租借设备{name}的申请'.format(username=appl.applicant.username,
                                                                              name=appl.equipment.name))
            else:
                logs_add(user, 'Change', '拒绝用户{username}租借设备{name}的申请'.format(username=appl.applicant.username,
                                                                              name=appl.equipment.name))
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 租借者归还设备，终止申请
def loan_prefinish(request, id):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            try:
                appl = LoanApplication.objects.get(id=id)
            except:
                return HttpResponse(status=404, content=json.dumps({'error': 'no such application'}))
            else:
                if appl.status != 'approved' or appl.applicant != user:
                    return HttpResponse(status=400, content=json.dumps({'error': 'cannot return'}))
                else:
                    # 更新申请状态
                    appl.status = 'prefinish'
                    appl.save()
                    logs_add(user, 'Change', '归还设备{name}'.format(name=appl.equipment.name))
                    return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 提供者确认设备归还
def loan_finish(request, id):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            try:
                appl = LoanApplication.objects.get(id=id)
            except:
                return HttpResponse(status=404, content=json.dumps({'error': 'no such application'}))
            else:
                if appl.status != 'prefinish' or appl.equipment.owner != user:
                    return HttpResponse(status=400, content=json.dumps({'error': 'cannot return'}))
                else:
                    # 更新申请状态
                    appl.status = 'finished'
                    appl.save()
                    logs_add(user, 'Change', '确认用户{username}归还设备{name}'.format(username=appl.applicant.username,
                                                                               name=appl.equipment.name))
                    return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


def logs_add(user, type, detail):
    SystemLog.objects.create(type=type, operator=user, detail=detail)


def logs_search(request):
    if request.method == 'GET':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            if user.has_admin_privileges():
                ans = []
                if SystemLog.objects.exists():
                    for log in SystemLog.objects.all():
                        log_info = {'operator': log.operator.username, 'type': log.type,
                                    'time': log.operate_time.timestamp(),
                                    'detail': log.detail}
                        ans.append(log_info)
                return HttpResponse(status=200, content=json.dumps(ans))

            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permissions'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))


def mails_add(request):
    if request.method == 'POST':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            try:
                receiver_username = request.POST['receiver']
                detail = request.POST['detail']
                type = request.POST['type']
                try:
                    receiver = SystemUser.objects.get(username=receiver_username)
                    if type == 'Hint':
                        Mail.objects.create(sender=user, receiver=receiver, type=type, detail=detail)
                    else:
                        try:
                            ID = request.POST['relatedID']
                            Mail.objects.create(sender=user, receiver=receiver, type=type, detail=detail, relatedID=ID)
                        except KeyError:
                            return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
                    return HttpResponse(status=200)
                except SystemUser.DoesNotExist:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no such a user'}))
            except KeyError:
                return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


def mails_search(request):
    if request.method == 'GET':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            ans = []
            for mail in Mail.objects.filter(receiver=user):
                ans.append({'sender': mail.sender.username, 'time': mail.send_time.timestamp(), 'detail': mail.detail,
                            'status': mail.read,
                            'id': mail.pk, 'type': mail.type, 'relatedID': mail.relatedID})
            return HttpResponse(status=200, content=json.dumps(ans))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))


def mail_delete(request, id):
    if request.method == 'POST':
        if 'username' in request.session:
            user_name = request.session['username']
            try:
                mail = Mail.objects.get(pk=id)
                mail.delete()
                return HttpResponse(status=200)
            except Mail.DoesNotExist:
                return HttpResponse(status=400, content=json.dumps({'error': 'no such mail'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


def mail_confirm(request, id):
    if request.method == 'POST':
        if 'username' in request.session:
            try:
                mail = Mail.objects.get(pk=id)
                mail.read = True
                mail.save()
                return HttpResponse(status=200)
            except Mail.DoesNotExist:
                return HttpResponse(status=400, content=json.dumps({'error': 'no such mail'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))

def admin_statistics(request):
    if request.method == 'GET':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            if user.has_admin_privileges():
                user_count = SystemUser.objects.all().count()
                provider_count = SystemUser.objects.filter(role='provider').count()
                devices_count = Equipment.objects.all().count()
                on_shelf_count = Equipment.objects.filter(status='on_shelf').count()
                wait_on_shelf_count = Equipment.objects.filter(status='wait_on_shelf').count()
                appls_count = LoanApplication.objects.all().count()
                appls_approved_count = (
                    LoanApplication.objects.filter(status='approved') |
                    LoanApplication.objects.filter(status='prefinish') |
                    LoanApplication.objects.filter(status='finished')
                ).count()
                appls_pending_count = LoanApplication.objects.filter(status='pending').count()
                last_week_appls_count = LoanApplication.objects.filter(
                    end_time__gte=datetime.now() - timedelta(days=7),
                    end_time__lt=datetime.now()
                ).count()
                next_week_appls_count = LoanApplication.objects.filter(
                    start_time__gte=datetime.now(),
                    start_time__lt=datetime.now() + timedelta(days=7)
                ).count()
                return HttpResponse(status=200, content=json.dumps({
                    'user_count': user_count,
                    'provider_count': provider_count,
                    'devices_count': devices_count,
                    'on_shelf_count': on_shelf_count,
                    'wait_on_shelf_count': wait_on_shelf_count,
                    'appls_count': appls_count,
                    'appls_approved_count': appls_approved_count,
                    'appls_pending_count': appls_pending_count,
                    'last_week_appls_count': last_week_appls_count,
                    'next_week_appls_count': next_week_appls_count,
                }))
            else:
                return HttpResponse(status=401, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET method'}))
