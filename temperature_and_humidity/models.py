from django.db import models

class TemperatureAndHumidityRecord(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    record_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'temperature_and_humidity_record'