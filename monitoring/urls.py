from django.conf.urls.static import static
from django.urls import path
from monitoring.views import *

app_name = 'monitoring'

urlpatterns = [
                  path('get_monitoring_display_and_detect_data/', GetMonitoringAndData.as_view(), name='get_monitoring_display_and_detect_data'),
                  path('update_monitoring_display_and_item/', UpdateMonitoringDisplayAndItem.as_view(), name='update_monitoring_display_and_item'),
                  path('update_temperature_and_humidity/', UpdateTemperatureAndHumidity.as_view(),
                       name='update_temperature_and_humidity'),
                  path('get_monitoring_record/', GetMonitoringRecord.as_view(), name='get_monitoring_record'),
                  path('get_monitoring_record/<int:page>', GetMonitoringRecord.as_view(), name='get_monitoring_record'),
              ]
