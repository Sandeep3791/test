# Suppliers Registration and Management Start
from django.shortcuts import render, redirect
from django.contrib import messages
from wayrem_admin.forms import SupplierRegisterForm, SupplierRegisterUpdateForm
import string
import secrets
from wayrem_admin.services import send_email
from wayrem_admin.export import generate_pdf, generate_excel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.models import SupplierRegister
from django.views import View


def supplier_excel(request):
    return generate_excel("supplier_master", "suppliers")


def supplier_pdf(request):
    query = 'SELECT username, email, contact, address, delivery_incharge, company_name, is_active FROM supplier_master'
    template = "pdf_supplier.html"
    file = "supplier.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


@login_required(login_url='/')
def supplier_register(request):

    if request.user.is_authenticated:
        alphabet = string.ascii_letters + string.digits
        auto_password = ''.join(secrets.choice(alphabet) for i in range(8))
        if request.method == 'POST':
            form = SupplierRegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                category_name = form.cleaned_data['category_name']
                user = SupplierRegister(
                    username=username, email=email, password=password)
                user.save()
                user.category_name.set(category_name)
                user.save()
                # form.save()

                to = email
                subject = 'Welcome to Wayrem Supplier'
                body = f'Your credential for <strong> Wayrem Supplier</strong> are:\n <br> Username: <em>{username}</em>\n  <br> Password: <em>{password}</em>\n <br> Email: <em>{email}</em>\n'
                # Role: {role}
                send_email(to, subject, body)
                messages.success(request, 'Supplier Created Successfully!!')
                return redirect('wayrem_admin:supplierlist')
        else:
            form = SupplierRegisterForm(
                initial={'password': auto_password, 'password2': auto_password})
        return render(request, 'accounts/supplier_register.html', {"form": form})
    else:
        return redirect('wayrem_admin:dashboard')


class SupplierList(View):
    template_name = "supplierlist.html"

    @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        supplierlist = SupplierRegister.objects.all()
        return render(request, self.template_name, {"supplierlist": supplierlist})


class DeleteSupplier(View):
    def post(self, request):
        supplierid = request.POST.get('supplier_id')
        user = SupplierRegister.objects.get(pk=supplierid)
        user.delete()
        return redirect('wayrem_admin:supplierlist')


# Active/Block
class Active_BlockSupplier(View):

    @method_decorator(login_required(login_url='/'))
    def get(self, request, id):
        user = SupplierRegister.objects.get(pk=id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('wayrem_admin:supplierlist')


def update_supplier(request, id=None):
    print(id)
    if request.method == "POST":
        # kwargs = { 'data' : request.POST }
        suppl = SupplierRegister.objects.get(id=id)
        form = SupplierRegisterUpdateForm(request.POST or None, instance=suppl)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            category_name = form.cleaned_data['category_name']
            print("FORM")
            suppl.username = username
            suppl.email = email
            suppl.category_name.set(category_name)
            suppl.save()
            return redirect('wayrem_admin:supplierlist')
    suppl = SupplierRegister.objects.get(id=id)
    form = SupplierRegisterUpdateForm(instance=suppl)
    return render(request, 'update_supplier.html', {'form': form, 'id': suppl.id})


def supplier_details(request, id=None):
    suppl = SupplierRegister.objects.filter(id=id).first()
    return render(request, 'supplier_popup.html', {'suppldata': suppl})

# Suppliers Registration and Management End
