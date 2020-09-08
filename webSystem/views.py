from django.shortcuts import render

from .models import SystemUser
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
            user.is_student=True
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
            if user_name is '' or password is '':
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
                return HttpResponse(status=400,content=json.dumps({'error': 'no such a user'}))
    else:
        return HttpResponse(status=400,content=json.dumps({'error': 'require POST'}))


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
            return HttpResponse(status=200,content=json.dumps({'user': user_name}))
        else:
            return HttpResponse(status=400,content=json.dumps({'error': 'no valid session'}))
    else:
        return HttpResponse(status=400,content=json.dumps({'error': 'require POST'}))


