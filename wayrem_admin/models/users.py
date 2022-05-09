from wayrem_admin.models.StaticModels import User
from django.contrib.auth.models import (BaseUserManager, _user_has_perm)
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from wayrem_admin.utils.constants import *
#from models_orders import Orders,OrderDetails

# Create your models here.

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True, unique=True)
    po_notify = models.BooleanField(default=False, null=True, blank=True)
    order_notify = models.BooleanField(default=False, null=True, blank=True)
    margin_access = models.BooleanField(default=False, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    is_superuser = models.IntegerField(null=True, blank=True, default=1)
    is_active = models.IntegerField(null=True, blank=True, default=1)
    contact = models.CharField(
        max_length=12, null=True, unique=True, blank=False)
    role = models.ForeignKey(
        'Roles', on_delete=models.CASCADE, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default='M', null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    zip_code = models.CharField(max_length=15, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "wayrem_admin"
        abstract = True


class MyUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password=None):
        """
        Creates and saves a User with the given email, first name, last name and password.
        """
        if not first_name:
            raise ValueError('Users must have first name')
        if not last_name:
            raise ValueError('Users must have last name')

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=self.normalize_email(email),
        )
        user.role_id = 1
        user.is_active = 1
        user.set_password(password)
        user.is_superuser = 0
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, password):
        """
        Creates and saves a superuser with the given email,first name, last name and password.
        """
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        user.role_id = 1
        user.is_active = 1
        user.is_superuser = 1
        user.save(using=self._db)
        return user


class Users(User):
    objects = MyUserManager()
    USERNAME_FIELD = 'username'
    #REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if self.is_active == 1 and self.is_superuser == 1:
            return True

        # Otherwise we need to check the backends.

        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """

        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Yes, always
        return True

    class Meta:
        # app_label = "wayrem_admin"
        db_table = 'users_master'


# class Users(User):
#     objects = MyUserManager()
#     USERNAME_FIELD = 'username'

#     def __str__(self):
#         return self.username
class Otp(models.Model):
    email = models.EmailField()
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'otp'
