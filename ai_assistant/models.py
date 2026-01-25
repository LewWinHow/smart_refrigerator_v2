from django.db import models

from user.models import User


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sender = models.IntegerField(db_comment='1 = user, 2 = system')

    class Meta:
        db_table = 'chat'

class VoiceInteractionChat(models.Model):
    message = models.TextField()
    sender = models.IntegerField(db_comment='1 = user, 2 = system')
    class Meta:
        db_table = 'voice_interaction_chat'
