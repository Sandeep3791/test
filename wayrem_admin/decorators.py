from django.contrib import messages
from django.shortcuts import redirect


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.user.is_authenticated:
                if (request.user.role and allowed_roles in request.user.role.permission) or request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "Permission Denied")
                    return redirect('updateprofile')
        return wrap
    return decorator
