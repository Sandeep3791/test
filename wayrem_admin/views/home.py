import json
from wayrem_admin.models import Notification, User, Supplier, Products
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import RedirectView
from django.urls import reverse

from wayrem_admin.services import inst_Supplier


class RootUrlView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse('wayrem_admin:login')
        return reverse('wayrem_admin:dashboard')


@ login_required(login_url='wayrem_admin:root')
def dashboard(request):
    # notifications = list(notifications.values())
    # for dicts in notifications:
    #     for keys in dicts:
    #         if keys == 'supplier_id':
    #             dicts[keys] = str(inst_Supplier(dicts[keys]))
    #         dicts[keys] = str(dicts[keys])
    # request.session['notifications'] = notifications
    # request.session['notifications'] = list(
    #     notifications.values_list('id', 'message', 'status'))
    subadmins = User.objects.exclude(is_superuser=True)
    suppliers = Supplier.objects.all()
    products = Products.objects.all()
    context = {
        'subadmins': len(subadmins),
        'suppliers': len(suppliers),
        'products': len(products),
    }
    return render(request, 'dashboard.html', context)


def notification_delete(request, id):
    notify = Notification.objects.filter(id=id).first()
    notify.delete()
    return redirect('wayrem_admin:polist')
