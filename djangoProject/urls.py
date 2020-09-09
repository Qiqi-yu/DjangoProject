"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webSystem import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/logon', views.logon_request),
    path('users/login',views.login_request),
    path('users/logout',views.logout_request),
    path('equipment/search', views.equipment_search),
    path('provider/search', views.provider_equipment_search),
    path('users/apply_provider',views.apply_provider),
    path('admin/users/query',views.admin_users_query),
    path('users/info',views.users_info),
    path('admin/users/check/apply',views.admin_check_users_apply),
    path('users/confirm/apply',views.users_confirm_apply)
]
