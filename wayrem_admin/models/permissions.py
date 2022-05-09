from django.db import models


class FunctionMaster(models.Model):
    function_name = models.CharField(max_length=100)
    parent_id = models.IntegerField()
    menu_icon = models.CharField(max_length=200, blank=True, null=True)
    action_path = models.CharField(max_length=100, blank=True, null=True)
    codename = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=1)
    show_in_menu = models.CharField(max_length=3, blank=True, null=True)
    show_in_permission = models.CharField(max_length=3)
    #child_permission = models.CharField(max_length=3)
    display_order = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'function_master'


class RolePermissions(models.Model):
    role_id = models.IntegerField()
    function = models.ForeignKey('FunctionMaster', models.DO_NOTHING)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'role_permissions'


class UserPermissions(models.Model):
    user_id = models.BigIntegerField()
    function = models.ForeignKey('FunctionMaster', models.DO_NOTHING)

    class Meta:
        app_label = "wayrem_admin"
        db_table = 'users_master_user_permissions'
