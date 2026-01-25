import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from item.models import Item
from monitoring.models import MonitoringDisplay, MonitoringRecord
from temperature_and_humidity.models import TemperatureAndHumidityRecord
from utils.get_data import get_data_by_page
from utils.verify import verify_superuser


class GetMonitoringAndData(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        is_superuser = user.is_superuser
        monitoring_display = MonitoringDisplay.objects.all()

        item_list = Item.objects.all().order_by('-id')
        temperature_and_humidity_list = TemperatureAndHumidityRecord.objects.all()
        temperature_and_humidity = temperature_and_humidity_list.last()
        return render(request, 'monitoring/monitoring.html',
                      {'monitoring_display': monitoring_display, 'item_list': item_list,
                       'temperature_and_humidity': temperature_and_humidity, 'user': user, 'is_superuser':is_superuser,'order_by':'0'})

    def post(self, request):
        user = request.user
        is_superuser = user.is_superuser
        monitoring_display = MonitoringDisplay.objects.all()

        order_by = request.POST.get('order_by') or None
        if order_by == '1':
            item_list = Item.objects.all().order_by('id')
        else:
            item_list = Item.objects.all().order_by('-id')

        temperature_and_humidity_list = TemperatureAndHumidityRecord.objects.all()
        temperature_and_humidity = temperature_and_humidity_list.last()
        return render(request, 'monitoring/monitoring.html',
                      {'monitoring_display': monitoring_display, 'item_list': item_list,
                       'temperature_and_humidity': temperature_and_humidity, 'user': user,
                       'is_superuser': is_superuser,'order_by':order_by})


class UpdateMonitoringDisplayAndItem(LoginRequiredMixin, View):
    def get(self, request):
        monitoring_display = MonitoringDisplay.objects.last() if MonitoringDisplay.objects.exists() else None

        item_list = Item.objects.order_by('-id').all()
        data = {
            'monitoring_display': monitoring_display.image.url if monitoring_display else None,
            'user': request.user.username,
            'item_list': [
                {
                    'id': item.id,
                    'item': item.item,
                    'user': item.user,
                    'permissions': item.permissions,
                    'image': item.image.url,
                    'record_time': re.sub(r'\bAM\b', 'a.m.',
                                          re.sub(r'\bPM\b', 'p.m.',
                                                 item.record_time.strftime('%b. %#d, %Y, %#I:%M %p')))
                }
                for item in item_list
            ]
        }

        return JsonResponse(data)


class UpdateTemperatureAndHumidity(LoginRequiredMixin, View):
    def get(self, request):
        temperature_and_humidity = TemperatureAndHumidityRecord.objects.last()
        temperature = temperature_and_humidity.temperature if temperature_and_humidity else None
        humidity = temperature_and_humidity.humidity if temperature_and_humidity else None

        data = {
            'temperature': temperature,
            'humidity': humidity,
        }

        return JsonResponse(data)

class GetMonitoringRecord(LoginRequiredMixin, View):
    def get(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        detect_record_list = MonitoringRecord.objects.all().order_by('-id')
        detect_record_list = get_data_by_page(detect_record_list, page)[0]
        is_paginated = get_data_by_page(detect_record_list, page)[1]
        return render(request, 'monitoring/monitoring_record.html',
                      {'detect_record_list': detect_record_list,
                       'is_paginated': is_paginated, 'is_superuser': is_superuser})

    def post(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser
        if verify_superuser(user) is not True:
            return verify_superuser(user)

        filter_select = request.POST.get('filter_select') or None
        filter_input = request.POST.get('filter_input') or None
        filter_input_second = request.POST.get('filter_input_second') or None
        detect_record_list = MonitoringRecord.objects.all()
        order_by = request.POST.get('order_by') or None

        if filter_select:
            if filter_select == '1':
                detect_record_list = MonitoringRecord.objects.all()
            elif filter_select == '2':
                if filter_input:
                    detect_record_list = MonitoringRecord.objects.filter(item=filter_input).all()
            elif filter_select == '3':
                if filter_input and filter_input_second:
                    detect_record_list = MonitoringRecord.objects.filter(record_time__gte=filter_input,
                                                                         record_time__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    detect_record_list = MonitoringRecord.objects.filter(record_time__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    detect_record_list = MonitoringRecord.objects.filter(
                        record_time__lte=filter_input_second).all()

        if order_by and order_by == '1':
            detect_record_list = detect_record_list.order_by('id')
        else:
            detect_record_list = detect_record_list.order_by('-id')

        detect_record_list = get_data_by_page(detect_record_list, page)[0]
        is_paginated = get_data_by_page(detect_record_list, page)[1]
        return render(request, 'monitoring/monitoring_record.html',
                      {'detect_record_list': detect_record_list,
                       'is_paginated': is_paginated, 'filter_select': filter_select, 'filter_input': filter_input,
                       'filter_input_second': filter_input_second,
                       'order_by': order_by,'is_superuser': is_superuser})
