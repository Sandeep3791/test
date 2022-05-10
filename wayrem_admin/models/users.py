from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (BaseUserManager, _user_has_perm)
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
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
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
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
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


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
