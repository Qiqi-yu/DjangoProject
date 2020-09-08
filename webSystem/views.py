from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from .models import SystemUser


def logon_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if username == '' or password == '' or email == '':
            return HttpResponse(status=400, content='invalid parameters')
        elif SystemUser.objects.filter(username=username).exists():
            return HttpResponse(status=400, content='user exists')
        else:
            user = SystemUser()
            user.username = username
            user.set_password(password)
            user.save()
            return HttpResponse(status=200)
    else:
        return HttpResponse(status=400, content='require POST')
