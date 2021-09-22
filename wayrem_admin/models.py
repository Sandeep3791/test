from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class Roles(models.Model):
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.role


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    contact = models.CharField(max_length=12, null=True, blank=True)
    role = models.ForeignKey(
        Roles, on_delete=models.DO_NOTHING, null=True, blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []


class Otp(models.Model):
    email = models.EmailField()
    otp = models.IntegerField()
