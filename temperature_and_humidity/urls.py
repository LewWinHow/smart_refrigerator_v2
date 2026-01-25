from django.conf.urls.static import static
from django.urls import path
from monitoring.views import *
from temperature_and_humidity.views import ReceiveTemperatureAndHumidity, RecordOfTemperatureAndHumidity

app_name = 'temperature_and_humidity'

urlpatterns = [
                  path('receive_temperature_and_humidity/', ReceiveTemperatureAndHumidity.as_view(),
                       name='receive_temperature_and_humidity'),
                  path('temperature_and_humidity_record/', RecordOfTemperatureAndHumidity.as_view(),
                       name='temperature_and_humidity_record'),
                  path('temperature_and_humidity_record/<int:page>', RecordOfTemperatureAndHumidity.as_view(),
                       name='temperature_and_humidity_record'),
              ]
