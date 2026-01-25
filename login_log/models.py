from django.db import models


class LoginIP(models.Model):
    ip = models.GenericIPAddressField()
    system = models.CharField(max_length=150)
    device = models.CharField(max_length=150)
    is_bot = models.IntegerField(db_comment='0 = Not, 1 = Yes')
    failed_count = models.IntegerField(default=0)
    is_blacklist = models.IntegerField(default=0, db_comment='0 = Not, 1 = Yes')

    class Meta:
        db_table = 'login_ip'


class LoginRecord(models.Model):
    login_ip = models.ForeignKey('LoginIP', on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    status = models.IntegerField(db_comment='0 = Fail, 1 = Success')
    record_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'login_record'
