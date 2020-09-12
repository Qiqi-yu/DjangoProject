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
    path('users/verify/<str:username>/<str:code>', views.user_verify),
    path('users/login',views.login_request),
    path('users/logout',views.logout_request),
    path('users/apply_provider',views.apply_provider),
    path('admin/users/query',views.admin_users_query),
    path('users/info',views.users_info),
    path('admin/users/check/apply',views.admin_check_users_apply),
    path('users/confirm/apply',views.users_confirm_apply),
    path('provider/add', views.provider_equipment_add),
    path('provider/update/<int:id>', views.provider_equipment_update),
    path('provider/on-shelf-apply/<int:id>', views.provider_equipment_on_shelf),
    path('admin/users/<str:username>/delete',views.admin_users_delete),
    path('provider/undercarriage/<int:id>', views.provider_equipment_undercarriage),
    path('admin/equipment/check/apply/<int:id>',views.admin_check_equipment_apply),
    path('equipment/confirm/apply', views.equipment_confirm_apply),
    path('equipment/delete/<int:id>', views.equipment_delete),
    path('equipment/search/<str:role>', views.equipments_search),
    path('loan/create', views.loan_create),
    path('loan/my', views.loan_my),
    path('loan/my_equipments', views.loan_my_equipments),
    path('loan/list/<int:eid>', views.loan_list),
    path('loan/<int:id>/review', views.loan_review),
    path('equipment/<int:id>/detail', views.equipment_detail),
    path('loan/prefinish/<int:id>', views.loan_prefinish),
    path('loan/finish/<int:id>', views.loan_finish)
    path('logs/add',views.logs_add),
    path('logs/search',views.logs_search),
    path('mails/add',views.mails_add),
    path('mails/search',views.mails_search),
    path('mails/<int:id>/delete',views.mail_delete),
    path('mails/<int:id>/confirm',views.mail_confirm)
]
