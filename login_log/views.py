import random
import string
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.views import View

from utils.get_data import get_device_info, get_data_by_page
from .models import LoginRecord, LoginIP
from utils.verify import *


# Create your views here.
class IPOfLogin(LoginRequiredMixin, View):
    def get(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        login_ip_list = LoginIP.objects.all().order_by('-id')
        login_ip_list = get_data_by_page(login_ip_list, page)[0]
        is_paginated = get_data_by_page(login_ip_list, page)[1]
        return render(request, 'login_log/login_ip.html',
                      {'login_ip_list': login_ip_list, 'is_paginated': is_paginated,'is_superuser': is_superuser})

    def post(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        filter_select = request.POST.get('filter_select') or None
        filter_input = request.POST.get('filter_input') or None
        blacklist_select = request.POST.get('blacklist_select') or None
        login_ip_list = LoginIP.objects.all()
        order_by = request.POST.get('order_by') or None

        if filter_select:
            if filter_select == '1':
                login_ip_list = LoginIP.objects.all()
            elif filter_select == '2':
                if filter_input:
                    login_ip_list = LoginIP.objects.filter(id=filter_input).all()
            elif filter_select == '3':
                if blacklist_select:
                    login_ip_list = LoginIP.objects.filter(is_blacklist=blacklist_select).all()

        if order_by and order_by == '1':
            login_ip_list = login_ip_list.order_by('id')
        else:
            login_ip_list = login_ip_list.order_by('-id')

        login_ip_list = get_data_by_page(login_ip_list, page)[0]
        is_paginated = get_data_by_page(login_ip_list, page)[1]
        return render(request, 'login_log/login_ip.html',
                      {'login_ip_list': login_ip_list,
                       'is_paginated': is_paginated, 'filter_select': filter_select, 'filter_input': filter_input,
                       'blacklist_select': blacklist_select, 'order_by': order_by,'is_superuser':is_superuser})


class RecordOfLogin(LoginRequiredMixin, View):
    def get(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        login_record_list = LoginRecord.objects.all().order_by('-id')
        login_record_list = get_data_by_page(login_record_list, page)[0]
        is_paginated = get_data_by_page(login_record_list, page)[1]
        return render(request, 'login_log/login_record.html',
                      {'login_record_list': login_record_list, 'is_paginated': is_paginated, 'order_by':'0','is_superuser':is_superuser})

    def post(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        filter_select = request.POST.get('filter_select') or None
        filter_input = request.POST.get('filter_input') or None
        filter_input_second = request.POST.get('filter_input_second') or None
        status_select = request.POST.get('status_select') or None
        login_record_list = LoginRecord.objects.all()
        order_by = request.POST.get('order_by') or None

        if filter_select:
            if filter_select == '1':
                login_record_list = LoginRecord.objects.all()
            elif filter_select == '2':
                if filter_input:
                    login_record_list = LoginRecord.objects.filter(id=filter_input).all()
            elif filter_select == '3':
                if filter_input:
                    login_record_list = LoginRecord.objects.filter(login_ip_id=filter_input).all()
            elif filter_select == '4':
                if status_select:
                    login_record_list = LoginRecord.objects.filter(status=status_select).all()
            elif filter_select == '5':
                if filter_input and filter_input_second:
                    login_record_list = LoginRecord.objects.filter(record_time__gte=filter_input,
                                                                   record_time__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    login_record_list = LoginRecord.objects.filter(record_time__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    login_record_list = LoginRecord.objects.filter(
                        record_time__lte=filter_input_second).all()

        if order_by and order_by == '1':
            login_record_list = login_record_list.order_by('id')
        else:
            login_record_list = login_record_list.order_by('-id')

        login_record_list = get_data_by_page(login_record_list, page)[0]
        is_paginated = get_data_by_page(login_record_list, page)[1]
        return render(request, 'login_log/login_record.html',
                      {'login_record_list': login_record_list,
                       'is_paginated': is_paginated, 'filter_select': filter_select, 'filter_input': filter_input,
                       'filter_input_second': filter_input_second, 'status_select': status_select,
                       'order_by': order_by,'is_superuser':is_superuser })


class IPBlacklist(LoginRequiredMixin, View):
    def get(self, request, id):

        user = request.user

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        login_ip = LoginIP.objects.filter(id=id).first()
        if login_ip:
            if login_ip.is_blacklist:
                login_ip.is_blacklist = False
                login_ip.save()
            else:
                login_ip.is_blacklist = True
                login_ip.save()
            return redirect('login_log:login_ip')
        else:
            return hint_message(request, 'Login info not found.', 'account:login_ip')


class DeleteLoginIP(LoginRequiredMixin, View):
    def get(self, request, id):

        user = request.user

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        login_ip = LoginIP.objects.filter(id=id).first()

        if not login_ip:
            return hint_message(request, 'Login info not found.', 'account:login_ip')

        login_ip.delete()
        return redirect('login_log:login_ip')


class DeleteLoginRecord(LoginRequiredMixin, View):
    def get(self, request, id):

        user = request.user

        if verify_superuser(user) is not True:
            return verify_superuser(user)

        login_record = LoginRecord.objects.filter(id=id).first()
        if not login_record:
            return hint_message(request, 'Login info not found.', 'account:login_ip')
        login_record.delete()
        return redirect('login_log:login_record')
