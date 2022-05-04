from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

class LoginPermissionCheckMixin(LoginRequiredMixin, PermissionRequiredMixin):
    pass
    
    
    



