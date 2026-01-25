import datetime
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView

from temperature_and_humidity.models import TemperatureAndHumidityRecord
from utils.get_data import get_data_by_page
from utils.verify import verify_superuser


class RecordOfTemperatureAndHumidity(LoginRequiredMixin, View):
    def get(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser

        datetime_now = datetime.datetime.now()
        datetime_today_midnight = datetime_now.replace(hour=0, minute=0, second=0, microsecond=0)
        datetime_next_day_midnight = datetime_today_midnight + datetime.timedelta(days=1)
        temperature_and_humidity_record_list_by_time = TemperatureAndHumidityRecord.objects.filter(
            record_time__gte=datetime_today_midnight, record_time__lt=datetime_next_day_midnight).all()

        times = []
        temperatures = []
        humiditys = []

        for temperature_and_humidity_record in temperature_and_humidity_record_list_by_time:
            times.append(temperature_and_humidity_record.record_time.strftime('%Y-%m-%d %H:%M:%S'))
            temperatures.append(temperature_and_humidity_record.temperature)
            humiditys.append(temperature_and_humidity_record.humidity)

        data = {
            'times': times,
            'temperatures': temperatures,
            'humiditys': humiditys
        }

        temperature_and_humidity_record_list = TemperatureAndHumidityRecord.objects.all().order_by('-id')
        temperature_and_humidity_record_list = get_data_by_page(temperature_and_humidity_record_list, page)[0]
        is_paginated = get_data_by_page(temperature_and_humidity_record_list, page)[1]
        return render(request, 'temperature_humidity/temperature_and_humidity_record.html',
                      {
                       'temperature_and_humidity_record_list': temperature_and_humidity_record_list,
                       'is_paginated': is_paginated, 'data': data,'is_superuser': is_superuser})

    def post(self, request, page=1):

        user = request.user
        is_superuser = user.is_superuser

        filter_select = request.POST.get('filter_select') or None
        filter_input = request.POST.get('filter_input') or None
        filter_input_second = request.POST.get('filter_input_second') or None
        temperature_and_humidity_record_list = TemperatureAndHumidityRecord.objects.all()
        order_by = request.POST.get('order_by') or None

        if filter_select:
            if filter_select == '1':
                temperature_and_humidity_record_list = TemperatureAndHumidityRecord.objects.all()
            elif filter_select == '2':
                if filter_input and filter_input_second:
                    temperature_and_humidity_record_list = TemperatureAndHumidityRecord.objects.filter(
                        record_time__gte=filter_input,
                        record_time__lte=filter_input_second).all()
                elif filter_input and filter_input_second is None:
                    temperature_and_humidity_record_list = TemperatureAndHumidityRecord.objects.filter(
                        record_time__gte=filter_input).all()
                elif filter_input is None and filter_input_second:
                    temperature_and_humidity_record_list = TemperatureAndHumidityRecord.objects.filter(
                        record_time__lte=filter_input_second).all()

        if order_by and order_by == '1':
            temperature_and_humidity_record_list = temperature_and_humidity_record_list.order_by('id')
        else:
            temperature_and_humidity_record_list = temperature_and_humidity_record_list.order_by('-id')

        temperature_and_humidity_record_list = get_data_by_page(temperature_and_humidity_record_list, page)[0]
        is_paginated = get_data_by_page(temperature_and_humidity_record_list, page)[1]

        datetime_now = datetime.datetime.now()
        datetime_today_midnight = datetime_now.replace(hour=0, minute=0, second=0, microsecond=0)
        datetime_next_day_midnight = datetime_today_midnight + datetime.timedelta(days=1)
        temperature_and_humidity_record_list_by_time = TemperatureAndHumidityRecord.objects.filter(
            record_time__gte=datetime_today_midnight, record_time__lt=datetime_next_day_midnight).all()

        times = []
        temperatures = []
        humiditys = []

        for temperature_and_humidity_record in temperature_and_humidity_record_list_by_time:
            times.append(temperature_and_humidity_record.record_time.strftime('%Y-%m-%d %H:%M:%S'))
            temperatures.append(temperature_and_humidity_record.temperature)
            humiditys.append(temperature_and_humidity_record.humidity)

        data = {
            'times': times,
            'temperatures': temperatures,
            'humiditys': humiditys
        }

        return render(request, 'temperature_humidity/temperature_and_humidity_record.html',
                      {
                       'temperature_and_humidity_record_list': temperature_and_humidity_record_list,
                       'is_paginated': is_paginated, 'filter_select': filter_select, 'filter_input': filter_input,
                       'filter_input_second': filter_input_second,
                       'order_by': order_by, 'data': data,'is_superuser': is_superuser})


class ReceiveTemperatureAndHumidity(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            temperature = data.get('temperature')
            humidity = data.get('humidity')

            if temperature and humidity:
                TemperatureAndHumidityRecord.objects.create(temperature=temperature, humidity=humidity)
                return JsonResponse({'status': 'saved'})
            else:
                return JsonResponse({'error': 'Invalid data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
