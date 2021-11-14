from wayrem_admin.models import CustomUser, SupplierRegister, Products
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import RedirectView
from django.urls import reverse


class RootUrlView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse('wayrem_admin:login')
        return reverse('wayrem_admin:dashboard')


@login_required(login_url='root')
def dashboard(request):
    subadmins = CustomUser.objects.exclude(is_superuser=True)
    suppliers = SupplierRegister.objects.all()
    products = Products.objects.all()
    context = {
        'subadmins': len(subadmins),
        'suppliers': len(suppliers),
        'products': len(products)
    }

    return render(request, 'dashboard.html', context)
