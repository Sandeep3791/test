# Suppliers Registration and Management Start
from django.shortcuts import render, redirect
from django.contrib import messages
from wayrem_admin.forms import SupplierForm, SupplierUpdateForm
import string
import secrets
from wayrem_admin.services import send_email
from wayrem_admin.export import generate_pdf, generate_excel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.models import Supplier
from django.views import View
from django.db import connection


def supplier_excel(request):
    return generate_excel("supplier_master", "suppliers")


def supplier_pdf(request):
    query = 'SELECT username, email, contact, address, delivery_incharge, company_name, is_active FROM supplier_master'
    template = "pdf_supplier.html"
    file = "supplier.pdf"
    return generate_pdf(query_string=query, template_name=template, file_name=file)


@login_required(login_url='wayrem_admin:root')
def supplier_register(request):

    if request.user.is_authenticated:
        alphabet = string.ascii_letters + string.digits
        auto_password = ''.join(secrets.choice(alphabet) for i in range(8))
        if request.method == 'POST':
            form = SupplierForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                company_name = form.cleaned_data['company_name']
                password = form.cleaned_data['password']
                category_name = form.cleaned_data['category_name']
                user = Supplier(
                    username=username, email=email, password=password, company_name=company_name)
                user.save()
                user.category_name.set(category_name)
                user.save()
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'CREATE TABLE If NOT Exists {username}_Invoice(`invoice_id` Varchar(250), `invoice_no` Varchar(250),`po_name` Varchar(250), `file` LONGBLOB , `supplier_name`  Varchar(250),`status` Varchar(250), `is active` boolean not null default 1 ,`created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL ,PRIMARY KEY(`invoice_id`));')
                    cursor.execute(
                        f'CREATE TABLE If NOT Exists {username}_purchase_order(`id` varchar(250) NOT NULL,`po_id` varchar(250) NOT NULL,`po_name` varchar(250) DEFAULT NULL,`product_qty` int NOT NULL,`status` varchar(250) DEFAULT NULL,`created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,`product_name_id` varchar(250) DEFAULT NULL,`supplier_name_id` varchar(250) NOT NULL,PRIMARY KEY (`id`),FOREIGN KEY (`product_name_id`) REFERENCES `products_master` (`id`), FOREIGN KEY (`supplier_name_id`) REFERENCES `supplier_master` (`id`));')
                to = email
                subject = 'Welcome to Wayrem Supplier'
                body = f'Your credential for <strong> Wayrem Supplier</strong> are:\n <br> Username: <em>{username}</em>\n  <br> Password: <em>{password}</em>\n <br> Email: <em>{email}</em>\n'
                # Role: {role}
                send_email(to, subject, body)
                messages.success(request, 'Supplier Created Successfully!!')
                return redirect('wayrem_admin:supplierlist')
        else:
            form = SupplierForm(
                initial={'password': auto_password, 'password2': auto_password})
        return render(request, 'accounts/supplier_register.html', {"form": form})
    else:
        return redirect('wayrem_admin:dashboard')


class SupplierList(View):
    template_name = "supplierlist.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, format=None):
        supplierlist = Supplier.objects.all()
        return render(request, self.template_name, {"supplierlist": supplierlist})


class DeleteSupplier(View):
    def post(self, request):
        supplierid = request.POST.get('supplier_id')
        user = Supplier.objects.get(pk=supplierid)
        user.delete()
        return redirect('wayrem_admin:supplierlist')


# Active/Block
class Active_BlockSupplier(View):

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, id):
        user = Supplier.objects.get(pk=id)
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
        suppl = Supplier.objects.get(id=id)
        form = SupplierUpdateForm(request.POST or None, instance=suppl)
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
    suppl = Supplier.objects.get(id=id)
    form = SupplierUpdateForm(instance=suppl)
    return render(request, 'update_supplier.html', {'form': form, 'id': suppl.id})


def supplier_details(request, id=None):
    suppl = Supplier.objects.filter(id=id).first()
    return render(request, 'supplier_popup.html', {'suppldata': suppl})
