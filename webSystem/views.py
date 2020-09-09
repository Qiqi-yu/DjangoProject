from django.shortcuts import render

from .models import SystemUser, Equipment
from django.http import HttpResponse
import json


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
            return HttpResponse(status=400, content=json.dumps({'error':'invalid parameters'}))
        # 判断用户名是否已经存在
        elif SystemUser.objects.filter(username=username).exists():
            return HttpResponse(status=400, content=json.dumps({'error':'user exists'}))
        else:
            user = SystemUser()
            # 先将用户类型设置为普通用户
            user.role = 'student'
            user.username = username
            user.set_password(password)
            user.save()
            return HttpResponse(status=200, content=json.dumps({'user':username}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error':'require POST'}))


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
            return HttpResponse(status=400,content=json.dumps({'error': 'no such a user'}))
        else:
            # 若用户名或密码为空
            if user_name == '' or password == '':
                return HttpResponse(status=400,content=json.dumps({'error': 'invalid parameters'}))
            try:
                # 获取用户信息
                user = SystemUser.objects.get(username=user_name)
                # 检查登录状态
                if user.logged:
                    return HttpResponse(status=400,content=json.dumps({'error': 'has logged in'}))
                else:
                    # 验证密码
                    if user.check_password(password):
                        # 设置Cookie
                        request.session['username'] = user_name
                        # 更新登录状态
                        user.logged = True
                        user.save()
                        return HttpResponse(status=200,content=json.dumps({'user': user_name}))
                    else:
                        return HttpResponse(status=400,content=json.dumps({'error': 'password is wrong'}))
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
            user = SystemUser.objects.get(username=user_name)
            # 更新登录状态
            user.logged = False
            user.save()
            del request.session['username']
            return HttpResponse(status=200, content=json.dumps({'user': user_name}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST'}))


# 用户查询所有上架的设备信息
def equipment_search(request):
    # 检验方法
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            ans = []
            for equipment in Equipment.objects.filter(status='on_shelf'):
                # 记录该设备的各项信息参数
                equipment_info = {'name': equipment.name, 'info': equipment.info,
                                'contact': [equipment.owner.info_lab, equipment.owner.info_address, equipment.owner.info_tel]}
                ans.append(equipment_info)
            return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
        else:
            return HttpResponse(status=400,content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400,content=json.dumps({'error': 'require GET'}))



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
                return HttpResponse(status=200, content=json.dumps({'name': name, 'info': info}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400,content=json.dumps({'error': 'require POST'}))


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


# 提供者查询己方设备信息
def provider_equipment_search(request):
    # 检验方法
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 检查用户是否具有该权限
            if user.has_provider_privileges():
                equipments = Equipment.objects.filter(owner=user)
                ans = []
                for equipment in equipments:
                    # 记录该设备的各项信息参数
                    equipment_info = {'name': equipment.name, 'info': equipment.info}
                    ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400,content=json.dumps({'error': 'require GET'}))


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
                        return HttpResponse(status=200, content=json.dumps({'name': equipment.name, 'info': equipment.info}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no provider permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400,content=json.dumps({'error': 'require POST'}))



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
                        examining=request.GET['examining']
                        users_data=[]
                        if SystemUser.objects.exists():
                            # 非审核状态下，返回所有数据
                            if examining == 'false':
                                for user in SystemUser.objects.all():
                                    users_data.append({'user_name':user.username,
                                                       'user_type':user.role,})
                            # 审核状态下，只返回需要审核的数据
                            elif examining == 'true':
                                query_set=SystemUser.objects.filter(examining_status='Examining')
                                if query_set.exists():
                                    for user in query_set.all():
                                        users_data.append({'user_name':user.username,
                                                           'user_type':user.role,'user_info_lab':user.info_lab,
                                                           'user_info_tel':user.info_tel,'user_info_address':user.info_address,
                                                           'user_info_description':user.info_description})
                        return HttpResponse(status=200,content=json.dumps(users_data))
                    except KeyError:
                        return HttpResponse(status=400,content=json.dumps({'error':'invalid parameters'}))
                else:
                    # print(user.role)
                    return HttpResponse(status=400,content=json.dumps({'error':'no permission'}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
        else:
            return HttpResponse(status=400,content=json.dumps({'error':'require GET method'}))


# 用户查询自己的信息
def users_info(request):
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 返回json数据
            user_data=[]
            user_data.append({'user_name': user.username,
                               'user_type': user.role,'user_examining':user.examining_status,
                                'user_info_lab': user.info_lab,
                               'user_info_tel': user.info_tel, 'user_info_address': user.info_address,
                               'user_info_description': user.info_description})
            return HttpResponse(status=200,content=json.dumps(user_data))
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
                    check_username=request.POST['username']
                    check_status = request.POST['pass']
                    # 同意
                    if check_status == 'true':
                        try:
                            apply_user=SystemUser.objects.get(username=check_username)
                            # 将e_s改为Pass 便于通知
                            apply_user.examining_status='Pass'
                            apply_user.role='provider'
                            apply_user.save()
                            return HttpResponse(status=200)
                        except SystemUser.DoesNotExist:
                            return HttpResponse(status=400,content=json.dumps({'error':'no such applyed user'}))
                    # 拒绝 需要理由
                    elif check_status == 'false':
                        try:
                            check_reason=request.POST['reason']
                            apply_user = SystemUser.objects.get(username=check_username)
                            # 将e_s改为拒绝 便于通知
                            apply_user.examining_status = 'Reject'
                            apply_user.info_reject=check_reason
                            apply_user.save()
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


# 用户确认申请审核状态的通知
def users_confirm_apply(request):
    if request.method == 'POST':
        if 'username' in request.session:
            user_name = request.session['username']
            user = SystemUser.objects.get(username=user_name)
            # 将examining_status恢复默认状态
            user.examining_status='Normal'
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
                        equipment.status = 'wait_on_shelf'
                        equipment.save()
                        return HttpResponse(status=200)
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))

    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require POST method'}))

