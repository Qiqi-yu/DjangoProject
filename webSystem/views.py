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
                # 检查登录状态
                if user.logged:
                    return HttpResponse(status=400, content=json.dumps({'error': 'has logged in'}))
                else:
                    # 验证密码
                    if user.check_password(password):
                        # 设置Cookie
                        request.session['username'] = user_name
                        # 更新登录状态
                        user.logged = True
                        user.save()
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


# 查询所有上架的设备信息
# TODO 接口测试
def equipment_search(request):
    # 检验方法
    if request.method == 'GET':
        # 检验会话状态
        if 'username' in request.session:
            # 找到所有的上架设备
            on_shelf_equipments = Equipment.objects.filter(status='on_shelf')
            equipments = []
            for equipment in on_shelf_equipments:
                # 记录该设备的各项信息参数
                equipment_info = {'name': equipment.name, 'description': equipment.description,
                                  'owner': equipment.owner.username,
                                  'contact': [equipment.owner.info_address, equipment.owner.info_tel]}
                equipments.append(equipment_info)
            return HttpResponse(status=200, content=json.dumps({'on_shelf_equipments': equipments}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET'}))



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
# TODO 接口测试
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
                    equipment_info = {'name': equipment.name, 'description': equipment.description}
                    ans.append(equipment_info)
                return HttpResponse(status=200, content=json.dumps({'equipments': ans}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'permission'}))
        else:
            return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400, content=json.dumps({'error': 'require GET'}))


# 管理查询所有用户
def users_query(request):
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
                    print(user.role)
                    return HttpResponse(status=400,content=json.dumps({'error':'no permission'}))
            else:
                return HttpResponse(status=400, content=json.dumps({'error': 'no valid session'}))
        else:
            return HttpResponse(status=400,content=json.dumps({'error':'require GET method'}))
