from wayrem_admin.users.models import Users
from wayrem_admin.permissions.models import *
import logging
from django.db.models import Q
from itertools import chain

class MyAuthBackend(object):
    def authenticate(self, request, username=None, password=None, **kwars):                
        try:
            user = Users.objects.get(username=username)            
            if user.check_password(password):
                return user
            else:
                return None
        except Users.DoesNotExist:
            #logging.getLogger("error_logger").error("user with login %s does not exists " % username)
            return None
        except Exception as e:
            #logging.getLogger("error_logger").error(repr(e))
            print(e)
            print("error")
            return None
    
    def get_user(self, user_id):
        try:
            user = Users.objects.get(id=user_id)
            if user.is_active == 1:
                return user
            return None
        except Users.DoesNotExist:
            #logging.getLogger("error_logger").error("user with %(id)d not found")
            return None    
        
    def _get_permissions(self, user_obj, obj, from_name):
        
        if user_obj.is_anonymous  or obj is not None:
            return set()
        
        perm_cache_name = '_%s_perm_cache' % from_name              
        if not hasattr(user_obj, perm_cache_name):
            perms = RolePermissions.objects.filter(role_id = user_obj.role.id)
            
            perms_list = perms.values_list('id', 'function__codename').order_by()
            parent_list = perms.filter(function__parent_id__gt= 0 ).values_list('function__parent_id').order_by() 
            #print("parent_list==",parent_list)
            fm_list = FunctionMaster.objects.filter(Q(id__in=parent_list)).values_list('id', 'codename')            
            #print("fm_list==",fm_list.query)
            if len(fm_list) > 0:
                perms_list = chain(fm_list, perms_list)
            setattr(user_obj, perm_cache_name, {"%s" % (name) for ct, name in perms_list})
        return getattr(user_obj, perm_cache_name)
    def get_user_permissions(self, user_obj, obj=None):
        return self._get_permissions(user_obj, obj, 'user')

    def get_all_permissions(self, user_obj, obj=None):
        
        if user_obj.is_active !=1 or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = {
                *self.get_user_permissions(user_obj),
                #*self.get_group_permissions(user_obj),
            }
        return user_obj._perm_cache

    def has_perm(self, user_obj, perm, obj=None):
        print(self.get_all_permissions(user_obj, obj))
        return user_obj.is_active == 1 and perm in self.get_all_permissions(user_obj, obj)
    