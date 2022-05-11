# Suppliers Registration and Management Start
import imp
from wayrem_admin.utils.constants import *
import uuid
from wayrem_admin.services import inst_Product, inst_Supplier
from wayrem_admin.models import PurchaseOrder
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from wayrem_admin.forms import SupplierForm, SupplierUpdateForm
import string
import secrets
from wayrem_admin.services import send_email
from wayrem_admin.export import generate_excel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.models import Supplier, SupplierProducts, BestProductsSupplier
from django.views import View
from django.db import connection
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
import uuid
import datetime
from wayrem_admin.models import PurchaseOrder, EmailTemplateModel
from wayrem_admin.services import inst_Product, inst_Supplier, inst_SupplierProduct

from wayrem_admin.views.product import product
from django.urls import reverse_lazy
from wayrem_admin.filters.supplier_filters import SupplierFilter
from django.views.generic import ListView
from wayrem_admin.forms.supplier import SupplierSearchFilter
from wayrem_admin.create_prefix_models import create_supplier_models_cluster
import os
from wayrem.settings import BASE_DIR


def supplier_excel(request):
    return generate_excel("supplier_master", "suppliers")


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
                # company_name = form.cleaned_data['company_name']
                password = form.cleaned_data['password']
                # category_name = form.cleaned_data['category_name']
                form.save()

                # user = Supplier(
                #     username=username, email=email, password=password, company_name=company_name)
                # user.save()
                # user.category_name.set(category_name)
                # user.save()
                # with connection.cursor() as cursor:
                #     cursor.execute(
                #         f'CREATE TABLE If NOT Exists {username}_Invoice(`invoice_id` Varchar(250), `invoice_no` Varchar(250),`po_name` Varchar(250), `file` LONGBLOB, `supplier_name`  Varchar(250),`status` Varchar(250), `is active` boolean not null default 1 ,`created_at` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL ,PRIMARY KEY(`invoice_id`));')
                #     cursor.execute(
                #         f'CREATE TABLE If NOT Exists {username}_purchase_order(`id` varchar(250) NOT NULL,`po_id` varchar(250) NOT NULL,`po_name` varchar(250) DEFAULT NULL,`product_qty` int NOT NULL,`status` varchar(250) DEFAULT NULL,`created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,`product_name_id` int(250) DEFAULT NULL,`supplier_name_id` int(250) NOT NULL,PRIMARY KEY (`id`),FOREIGN KEY (`product_name_id`) REFERENCES `products_master` (`id`), FOREIGN KEY (`supplier_name_id`) REFERENCES `supplier_master` (`id`));')
                to = email
                obj = EmailTemplateModel.objects.filter(
                    key='supplier_register').first()
                # subject = 'Welcome to Wayrem'
                values = {
                    'username': username,
                    'password': password,
                    'email': email,
                }
                subject = obj.subject
                body = obj.message_format.format(**values)
                # Role: {role}
                send_email(to, subject, body)
                create_supplier_models_cluster(username)
                file = str(BASE_DIR) + "/newmigration"
                print(os.path.exists(file))
                with open(file, mode='a'):
                    pass
                print(os.path.exists(file))
                messages.success(request, 'Supplier Created Successfully!!')
                return redirect('wayrem_admin:supplierlist')
        else:
            form = SupplierForm(
                initial={'password': auto_password, 'password2': auto_password})
        return render(request, 'accounts/supplier_register.html', {"form": form})
    else:
        return redirect('wayrem_admin:dashboard')


# class SupplierList(View):
#     template_name = "supplierlist.html"

#     @method_decorator(login_required(login_url='wayrem_admin:root'))
#     def get(self, request, format=None):
#         supplierlist = Supplier.objects.all()
#         paginator = Paginator(supplierlist, RECORDS_PER_PAGE)
#         page = request.GET.get('page')
#         try:
#             slist = paginator.page(page)
#         except PageNotAnInteger:
#             # If page is not an integer, deliver first page.
#             slist = paginator.page(1)
#         except EmptyPage:
#             # If page is out of range (e.g. 9999), deliver last page of results.
#             slist = paginator.page(paginator.num_pages)
#         return render(request, self.template_name, {"supplierlist": slist})


class SupplierList(ListView):
    model = Supplier
    template_name = "supplier/list.html"
    context_object_name = 'supplierlist'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:supplierlist')

    def get_queryset(self):
        qs = Supplier.objects.all()
        filtered_list = SupplierFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(SupplierList, self).get_context_data(**kwargs)
        context['filter_form'] = SupplierSearchFilter(self.request.GET)
        return context


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
            form.save()
            # username = form.cleaned_data['username']
            # email = form.cleaned_data['email']
            # category_name = form.cleaned_data['category_name']
            # print("FORM")
            # suppl.username = username
            # suppl.email = email
            # suppl.category_name.set(category_name)
            # suppl.save()
            return redirect('wayrem_admin:supplierlist')
    else:
        suppl = Supplier.objects.get(id=id)
        form = SupplierUpdateForm(instance=suppl)
    return render(request, 'update_supplier.html', {'form': form, 'id': suppl.id})


def supplier_details(request, id=None):
    suppl = Supplier.objects.filter(id=id).first()
    return render(request, 'supplier_popup.html', {'suppldata': suppl})


def allproductsupplier(request):
    supplierid = request.GET.get('supplierid')
    products = SupplierProducts.objects.filter(
        supplier_id_id=supplierid, product_id__is_deleted=False)
    product_list = []
    for product in products:
        product_list.append(product.product_id)
    best_product = []
    for i in product_list:
        data = BestProductsSupplier.objects.filter(product_id=i.id)
        data2 = [{'lowest_price': i.lowest_price, 'lowest_delivery_time':
                  i.lowest_delivery_time, 'supplier_id': i.supplier_id} for i in data]
        data2 = data2.pop()
        best_product.append(data2)
    print(best_product)
    list = zip(products, best_product)
    return render(request, 'supplier_viewall_product.html', {"list": list, 'supplier': supplierid})


def supplier_products_po(request):
    if request.method == "POST":
        supplier = request.POST.get('supplier')
        supplier_name = inst_Supplier(supplier)
        products = [v for k, v in request.POST.items() if k.startswith('prod')]
        request.session['products'] = []
        for prod in products:
            product_id = prod
            product_qty = 1
            name = inst_SupplierProduct(product_id)
            x = (product_id, name.product_name, name.price, product_qty)
            request.session['products'].append(x)
            po = request.session['products']
        request.session['supplier_company'] = supplier
        # request.session.modified = True
        print('add more')
        # po_id = uuid.uuid4()
        # # po_name = "PO"+str(random_no)
        # today = str(datetime.date.today())
        # curr_year = int(today[:4])
        # curr_month = int(today[5:7])
        # curr_date = int(today[8:10])
        # po = PurchaseOrder.objects.all()
        # aa = po.count()+1
        # q = ["{0:04}".format(aa)]
        # p = q[0]
        # po_name = "PO/"+str(curr_date) + \
        #     str(curr_month)+str(curr_year)+'/'+p
        # for data in products:
        #             supp_po_id = uuid.uuid4()
        #             print(data)
        #             product_instance = inst_Product(data)
        #             product_qty = 1
        #             with connection.cursor() as cursor:
        #                 cursor.execute(
        #                     f"INSERT INTO {supplier_name.username}_purchase_order(`id`,`po_id`,`po_name`,`product_qty`,`product_name_id`,`supplier_name_id`) VALUES('{supp_po_id}','{po_id}','{po_name}','{product_qty}','{product_instance.id.hex}','{supplier.replace('-','')}');")
        #                 product_order = PurchaseOrder(
        #                     po_id=po_id, po_name=po_name, product_name=product_instance, product_qty=product_qty, supplier_name=supplier_name)
        #             product_order.save()
        # return redirect("wayrem_admin:editpo",id=po_id)

        return redirect("wayrem_admin:create_po")


# def lowest_price_supplierview(request, id=None):
#     low_price = request.GET.get('lowest_price')
#     data = BestProductsSupplier.objects.filter(product_id = id, lowest_price = low_price)
#     for i in data:
#        supplierid = i.supplier_id
#     a = allproductsupplier(request,supplierid)
#     return 'success'
