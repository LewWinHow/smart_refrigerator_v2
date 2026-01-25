import pickle

import numpy as np
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    AbstractUser,
)


class User(AbstractUser):
    """
    -----AbstractUser-provided fields-----

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False) //Mean administration account
    is_active = models.BooleanField(default=True) //Mean account status
    is_superuser = models.BooleanField(default=False) //Mean supervisor account
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    """
    birthday = models.DateField(null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True, db_comment='1 = Male, 2 = Female')
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_image/')
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'


class FaceID(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    embedding = models.BinaryField(null=True)

    def set_embedding(self, emb: np.ndarray):
        self.embedding = pickle.dumps(emb.astype(np.float32))

    def get_embedding(self) -> np.ndarray:
        return pickle.loads(self.embedding)

    class Meta:
        db_table = 'face_id'
