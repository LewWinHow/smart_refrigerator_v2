from django.db import models

class MonitoringDisplay(models.Model):
    image = models.ImageField(upload_to='monitoring_display/')

    class Meta:
        db_table = 'monitoring_display'

class MonitoringRecord(models.Model):
    item = models.CharField(max_length=150)
    user = models.CharField(max_length=150)
    action = models.IntegerField(null=True, blank=True, db_comment='0 = take out, 1 = put in')
    image = models.ImageField(upload_to='monitoring_record/')
    record_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'monitoring_record'
