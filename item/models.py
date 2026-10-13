from django.db import models


class Item(models.Model):
    item = models.CharField(max_length=150)
    user = models.CharField(max_length=150)
    image = models.ImageField(upload_to='item/')
    permissions = models.IntegerField(default=0, db_comment='0 = private, 1 = public')
    record_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'item'
