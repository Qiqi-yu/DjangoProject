from django.shortcuts import render

from .models import SystemUser, Equipment, LoanApplication
from django.http import HttpResponse
import json
from datetime import datetime


# Create your views here.


# 注册接口
def logon_request(request):
    # 检验方法
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # TODO 邮箱认证

        # 判断参数名是否为空
        if username == '' or password == '' or email == '':
            return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
        # 判断用户名是否已经存在
        elif SystemUser.objects.filter(username=username).exists():
            return HttpResponse(status=400, content=json.dumps({'error': 'user exists'}))
        else:
            user = SystemUser()
            # 先将用户类型设置为普通用户
            user.role = 'student'
            user.username = username
            user.set_password(password)
            user.save()
            return HttpResponse(status=200, content=json.dumps({'user': username}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


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
                # 验证密码
                if user.check_password(password):
                    # 设置Cookie
                    request.session['username'] = user_name
                    return HttpResponse(status=200, content=json.dumps({'user': user_name}))
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


# 用户查询所有上架的设备信息
# def equipment_search(request):
#     # 检验方法
#     if request.method == 'GET':
#         # 检验会话状态
#         if 'username' in request.session:
#             ans = []
#             for equipment in Equipment.objects.filter(status='on_shelf'):
#                 # 记录该设备的各项信息参数
#                 equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info,
#                                 'contact': [equipment.owner.info_lab, equipment.owner.info_address, equipment.owner.info_tel]}
#                 ans.append(equipment_info)
#             return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
#         else:
#             return HttpResponse(status=400,content=json.dumps({'error': 'no valid session'}))
#     else:
#         return HttpResponse(status=400,content=json.dumps({'error': 'require GET'}))


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
                return HttpResponse(status=200, content=json.dumps({'id': equipment.id, 'name': name, 'info': info}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'permission'}))
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
            address = request.POST['info_tel']
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
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# # 提供者查询己方设备信息
# def provider_equipment_search(request):
#     # 检验方法
#     if request.method == 'GET':
#         # 检验会话状态
#         if 'username' in request.session:
#             user_name = request.session['username']
#             user = SystemUser.objects.get(username=user_name)
#             # 检查用户是否具有该权限
#             if user.has_provider_privileges():
#                 equipments = Equipment.objects.filter(owner=user)
#                 ans = []
#                 for equipment in equipments:
#                     # 记录该设备的各项信息参数
#                     equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info}
#                     ans.append(equipment_info)
#                 return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
#             else:
#                 return HttpResponse(status=400, content=json.dumps({'error': 'permission'}))
#         else:
#             return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
#     else:
#         return HttpResponse(status=400,content=json.dumps({'error': 'require GET'}))


# 提供者修改己方设备信息
def provider_equipment_update(request, id):
    # 检验方法
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_provider_privileges():
                try:
                    equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
                else:
                    if equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif equipment.status != 'exist':
                        return HttpResponse(status=400, content=json.dumps({'error': 'already on shelf'}))
                    else:
                        name = request.POST.get('name')
                        info = request.POST.get('info')
                        equipment.name = name if name else equipment.name
                        equipment.info = info if info else equipment.info
                        equipment.save()
                        return HttpResponse(status=200, content=json.dumps({'id': equipment.id, 'name': equipment.name, 'info': equipment.info}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no provider permission'}))
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
            user_data = [{'user_name': user.username,
                          'user_type': user.role, 'user_examining': user.examining_status,
                          'user_info_lab': user.info_lab,
                          'user_info_tel': user.info_tel, 'user_info_address': user.info_address,
                          'user_info_description': user.info_description}]
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
            if user.has_provider_privileges():
                try:
                    equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
                else:
                    if equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif equipment.status != 'exist':
                        return HttpResponse(status=400, content=json.dumps({'error': 'cannot apply'}))
                    else:
                        equipment.examining_status='examining'
                        equipment.status = 'wait_on_shelf'
                        equipment.save()
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
            if user.has_provider_privileges():
                try:
                    equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400, content=json.dumps({'error': 'no equipment'}))
                else:
                    if equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif equipment.status != 'on_shelf':
                        return HttpResponse(status=400, content=json.dumps({'error': 'cannot apply'}))
                    else:
                        equipment.status = 'exist'
                        equipment.save()
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
                            equipment.examining_status='pass'
                            equipment.status = 'on_shelf'
                            equipment.save()
                            return HttpResponse(status=200)
                        except Equipment.DoesNotExist:
                            return HttpResponse(status=400,content=json.dumps({'error':'no such applyed equipment'}))
                    # 拒绝 需要理由
                    elif check_status == 'false':
                        try:
                            check_reason=request.POST['reason']
                            equipment = Equipment.objects.get(id=id)
                            # 将e_s改为拒绝 便于通知
                            equipment.examining_status = 'Reject'
                            equipment.info_reject=check_reason
                            equipment.save()
                            return HttpResponse(status=200)
                        except KeyError:
                            return HttpResponse(status=400,content=json.dumps({'error':'invalid parameters'}))
                except KeyError:
                    return HttpResponse(status=400, content=json.dumps({'error': 'invalid parameters'}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 用户确认设备审核状态的通知
def equipment_confirm_apply(request):
    if request.method == 'POST':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 将examining_status恢复默认状态
            equipments = Equipment.objects.filter(owner=user, examining_status='pass' or 'reject')
            for equipment in equipments:
                equipment.examining_status = 'Normal'
                equipment.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


# 简单的删除用户
def admin_users_delete(request,username):
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
                    # TODO:如果需要保留历史租借申请 需要更改级联删除 通过搜素完成
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


# 提供者删除设备
def equipment_delete(request, id):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_provider_privileges():
                try:
                    delete_equipment = Equipment.objects.get(id=id)
                except:
                    return HttpResponse(status=400,content=json.dumps({'error':'no such equipment'}))
                else:
                    if delete_equipment.owner != user:
                        return HttpResponse(status=400, content=json.dumps({'error': 'not its owner'}))
                    elif delete_equipment.status == 'exist' or delete_equipment.status == 'wait_on_shelf':
                        return HttpResponse(status=400, content=json.dumps({'error': 'cannot delete'}))
                    else:
                        delete_equipment.delete()
                        return HttpResponse(status=200)
            else:
                return HttpResponse(status=400,content=json.dumps({'error':'no permissions'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


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
                for equipment in Equipment.objects.All():
                    # 记录该设备的各项信息参数
                    equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info,'status': equipment.status,
                                      'contact': [equipment.owner.name, equipment.owner.info_lab, equipment.owner.info_address,
                                                  equipment.owner.info_tel]}
                    ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            # 提供者查询己方所有设备
            elif role == 'provider' and user.has_provider_privileges():
                equipments = Equipment.objects.filter(owner=user)
                ans = []
                for equipment in equipments:
                    # 记录该设备的各项信息参数
                    equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info, 'status':equipment.status}
                    ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            # 普通用户或提供者查询所有上架设备
            elif role == 'student' and user.has_student_privileges():
                ans = []
                for equipment in Equipment.objects.filter(status='on_shelf'):
                    # 记录该设备的各项信息参数
                    equipment_info = {'id': equipment.id, 'name': equipment.name, 'info': equipment.info,
                                      'contact': [equipment.owner.username, equipment.owner.info_lab, equipment.owner.info_address,
                                                  equipment.owner.info_tel]}
                    ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permissions'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET'}))


def loan_create(request):
    if request.method == 'POST':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            try:
                eid = int(request.POST['equipment'])
                start_time = datetime.utcfromtimestamp(int(request.POST['start_time']))
                end_time = datetime.utcfromtimestamp(int(request.POST['end_time']))
                statement = request.POST['statement']
            except:
                return HttpResponse(status=400, content=json.dumps({'error': 'Incorrect format'}))
            try:
                equipment = Equipment.objects.get(id=eid)
            except SystemUser.DoesNotExist:
                return HttpResponse(status=404, content=json.dumps({'error': 'no such equipment'}))
            # TODO: 检查设备是否已上架且未被占用
            appl = LoanApplication()
            appl.applicant = user
            appl.equipment = equipment
            appl.start_time = start_time
            appl.end_time = end_time
            appl.statement = statement
            appl.save()
            return HttpResponse(status=200, content=json.dumps({'id': appl.id}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))


def _appl_json_object(appl):
    return {
        'id': appl.id,
        'status': appl.status,
        'equipment': {
            'id': appl.equipment.id,
            'name': appl.equipment.name,
        },
        'start_time': datetime.timestamp(appl.start_time),
        'end_time': datetime.timestamp(appl.end_time),
        'statement': appl.statement,
        'response': appl.response,
    }

def loan_my(request):
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 查找自己发起的所有申请
            appls = list(map(_appl_json_object, LoanApplication.objects.filter(applicant=user)))
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
            try:
                appl = LoanApplication.objects.get(id=id)
            except LoanApplication.DoesNotExist:
                return HttpResponse(status=404, content=json.dumps({'error': 'no such application'}))
            if appl.equipment.owner != user:
                return HttpResponse(status=401, content=json.dumps({'error': 'not its owner'}))
            try:
                accept = int(request.POST['accept'])
                response = request.POST['response']
            except:
                return HttpResponse(status=400, content=json.dumps({'error': 'Incorrect format'}))
            # TODO: 检查设备是否上架且未被占用
            # 更新申请状态
            appl.status = 'approved' if accept != 0 else 'rejected'
            appl.response = response
            appl.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))
