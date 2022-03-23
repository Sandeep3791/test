from django.apps import apps
import datetime
import imp
from django.urls import reverse_lazy
from django.views.generic import ListView
from wayrem_admin.filters.po_filters import *
from wayrem_admin.utils.constants import *
import re
from typing import Set
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from wayrem_admin.models import EmailTemplateModel, Notification, PO_log, PurchaseOrder, Products, Settings, Supplier, SupplierProducts, Inventory
from wayrem_admin.forms import POForm, POEditForm, POSearchFilter, POFormOne
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wayrem_admin.services import inst_Product, inst_Supplier, inst_SupplierProduct, inst_Product_SKU, delSession, send_email
from wayrem_admin.export import generate_excel
from wayrem_admin.decorators import role_required
import datetime
import uuid
from django.db import connection
from django.http import HttpResponse
# pdf export
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from wayrem_admin.models_recurrence import ForecastJobtype
from django.core import serializers


def po_excel(request):
    return generate_excel("po_master", "purchase_order")


@role_required('Purchase Order Add')
def create_purchase_order(request):
    if request.method == "POST":
        form = POFormOne(request.POST or None, request.FILES or None)
        if 'addMore' in request.POST:
            if request.POST['product_name'] == "":
                messages.error(request, "Please select a Product!")
                return redirect("wayrem_admin:create_po")
            product_id = request.POST['product_name']
            product_qty = request.POST['product_qty']
            name = inst_SupplierProduct(product_id)
            try:
                if any(e[0] == product_id for e in request.session.get('products')):
                    messages.error(request, "Product already added!")
                    return redirect("wayrem_admin:create_po")
            except:
                pass
            x = (product_id, name.product_name, name.price, product_qty)
            request.session['products'].append(x)
            po = request.session['products']
            request.session['supplier_company'] = request.POST['supplier_name']
            request.session.modified = True
            print('add more')
            forecast_day = ForecastJobtype.objects.filter(status=1)
            return render(request, "po_step1.html", {'form': form, 'po': po, 'forecast_day': forecast_day})
        elif 'send' in request.POST:
            if request.POST['supplier_name'] == '':
                messages.error(request, "Please Select Supplier!")
                return render(request, "po_step1.html", {'form': form, 'po': request.session['products']})
            if request.session['products'] == []:
                messages.error(request, "Please select some Products!")
                return redirect("wayrem_admin:create_po")
            else:
                print("supplier")
                supplier_name = inst_Supplier(request.POST['supplier_name'])
                x = request.POST['supplier_name']
                # random_no = random.randint(1000, 99999)
                po_id = uuid.uuid4()
                # po_name = "PO"+str(random_no)
                today = str(datetime.date.today())
                curr_year = int(today[:4])
                curr_month = int(today[5:7])
                curr_date = int(today[8:10])
                po = PurchaseOrder.objects.all()
                aa = po.count()+1
                q = ["{0:04}".format(aa)]
                p = q[0]
                po_name = "PO/"+str(curr_date) + \
                    str(curr_month)+str(curr_year)+'/'+p

                for data in request.session['products']:
                    supp_po_id = uuid.uuid4()
                    print(data)
                    product_instance = inst_Product(data[0])
                    product_qty = data[2]
                    supplier_purchase_model = str(
                        supplier_name) + '_purchase_order'
                    supplier = apps.get_model(
                        app_label='wayrem_admin', model_name=supplier_purchase_model)
                    supplier_po = supplier(po_id=po_id, po_name=po_name, product_name=product_instance,
                                           product_qty=product_qty, supplier_name=supplier_name)
                    supplier_po.save()
                    # with connection.cursor() as cursor:
                    #     cursor.execute(
                    #         f"INSERT INTO {supplier_name.username}_purchase_order(`id`,`po_id`,`po_name`,`product_qty`,`product_name_id`,`supplier_name_id`) VALUES('{supp_po_id}','{po_id}','{po_name}','{data[2]}','{product_instance.id.hex}','{x.replace('-','')}');")
                    product_order = PurchaseOrder(
                        po_id=po_id, po_name=po_name, product_name=product_instance, product_qty=product_qty, supplier_name=supplier_name)
                    product_order.save()
                messages.success(
                    request, f"Purchase Order Created Successfully!")
                request.session['products'] = []
                return redirect('wayrem_admin:polist')
        else:
            print("Invalid")
    else:
        if request.GET.get('supplier'):
            form = POFormOne(
                initial={"supplier_name": request.GET.get('supplier')})
        elif request.GET.get('product'):
            prod = request.GET.get('product')
            try:
                p = SupplierProducts.objects.filter(SKU=prod).first().id
            except:
                p = 1
            form = POFormOne(
                initial={"product_name": p})
        elif request.GET.get('suprod'):
            x = request.GET.get('suprod').split('?')
            product = SupplierProducts.objects.filter(SKU=x[1]).first()
            form = POFormOne(
                initial={"product_name": product, "supplier_name": x[0]})
        else:
            form = POFormOne(
                initial={'supplier_name': request.session.get('supplier_company', None)})
    po = request.session.get('products', None)
    forecast_day = ForecastJobtype.objects.filter(status=1)
    return render(request, "po_step1.html", {'form': form, "po": po, 'forecast_day': forecast_day})


def create_po_step2(request):
    if request.method == "POST":
        if request.session['products'] == []:
            messages.error(request, "Please select some Products!")
            return redirect("wayrem_admin:create_po")
        else:
            print("supplier")
            x = request.session.get('supplier_company')
            supplier_name = inst_Supplier(
                request.session.get('supplier_company'))
            # x = request.POST['supplier_name']
            # random_no = random.randint(1000, 99999)
            po_id = uuid.uuid4()
            # po_name = "PO"+str(random_no)
            today = str(datetime.date.today())
            curr_year = int(today[:4])
            curr_month = int(today[5:7])
            curr_date = int(today[8:10])
            po = PurchaseOrder.objects.all()
            aa = po.count()+1
            q = ["{0:04}".format(aa)]
            p = q[0]
            po_name = "PO/"+str(curr_date) + \
                str(curr_month)+str(curr_year)+'/'+p
            products = [v for k, v in request.POST.items()
                        if k.startswith('product')]
            quantities = [v for k, v in request.POST.items()
                          if k.startswith('quantity')]

            for product, quantity in zip(products, quantities):
                supp_po_id = uuid.uuid4()
                print(product)
                supplier_product_instance = inst_SupplierProduct(product)
                product_instance = inst_Product_SKU(
                    supplier_product_instance.SKU)
                product_qty = quantity
                supplier_purchase_model = 'PurchaseOrder_' + \
                    str(supplier_name.username)
                supplier = apps.get_model(
                    app_label='wayrem_admin', model_name=supplier_purchase_model)
                supplier_po = supplier(po_id=po_id, po_name=po_name, product_name=product_instance,
                                       product_qty=product_qty, supplier_name=supplier_name)
                supplier_po.save()
                # with connection.cursor() as cursor:
                #     cursor.execute(
                #         f"INSERT INTO {supplier_name.username}_purchase_order(`id`,`po_id`,`po_name`,`product_qty`,`product_name_id`,`supplier_name_id`) VALUES('{supp_po_id}','{po_id}','{po_name}','{quantity}','{product_instance.id}','{x.replace('-','')}');")
                product_order = PurchaseOrder(
                    po_id=po_id, po_name=po_name, product_name=product_instance, supplier_product=supplier_product_instance, product_qty=product_qty, supplier_name=supplier_name)
                product_order.save()
            # sending notification
            setting = Settings.objects.filter(
                key="notification_supplier").first()
            message = setting.value
            msg = message.format(number=po_name)
            notify = Notification(
                message=msg, supplier=supplier_name)
            notify.save()
            # sending mail to supplier
            email_setting = EmailTemplateModel.objects.filter(
                key="po_create").first()
            body = email_setting.message_format.format(number=po_name)
            to = supplier_name.email
            subject = email_setting.subject.format(number=po_name)
            send_email(to, subject, body)
            messages.success(
                request, f"Purchase order created successfully!")
            request.session['products'] = []
            return redirect('wayrem_admin:polist')
    else:
        pass


def delete_inserted_item(request, id=None):
    product = request.session.get("products")
    for index, num_list in enumerate(product):
        if num_list[0] == id:
            del product[index]
            break
    print(product)
    request.session["products"] = product
    return redirect('wayrem_admin:create_po')


class POList(ListView):
    model = PurchaseOrder
    template_name = "purchase_order/list.html"
    context_object_name = 'list'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:polist')

    def get_queryset(self):
        qs = PurchaseOrder.objects.filter().values(
            'po_name', 'supplier_name__company_name', 'po_id', 'status').distinct()
        filtered_list = POFilter(self.request.GET, queryset=qs)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        delSession(self.request)
        self.request.session['products'] = []
        context = super(POList, self).get_context_data(**kwargs)
        context['filter_form'] = POSearchFilter(self.request.GET)
        return context


class POList1(View):
    template_name = "po_list.html"

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    @method_decorator(role_required('Purchase Order View'))
    def get(self, request, format=None):
        delSession(request)
        # polist = PurchaseOrder.objects.values(
        #     'po_id', 'po_name', 'supplier_name', 'status').distinct()
        po = PurchaseOrder.objects.values(
            'po_name', 'supplier_name', 'po_id', 'status').distinct()
        # po = PurchaseOrder.objects.all().order_by('po_name').distinct()
        paginator = Paginator(po, 25)
        page = request.GET.get('page')
        try:
            ulist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            ulist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            ulist = paginator.page(paginator.num_pages)
        # pol = []
        # for i in polist:
        #     obj = Supplier.objects.filter(
        #         id=i['supplier_name']).first()
        #     pol.append(obj.username)
        # mylist = zip(polist, pol)
        # polist = PurchaseOrder.objects.values_list('po_id').distinct()
        # polist = PurchaseOrder.objects.distinct('po_id')
        request.session['products'] = []
        return render(request, self.template_name, {"list": ulist})


class DeletePO(View):

    @method_decorator(role_required('Purchase Order Delete'))
    def post(self, request):
        po_id = request.POST.get('po_id')
        po_obj = PurchaseOrder.objects.filter(po_id=po_id).all()
        po_obj.delete()
        return redirect('wayrem_admin:polist')


@role_required('Purchase Order View')
def viewpo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    poname = po[0].po_name
    po_log = PO_log.objects.filter(po=poname).order_by('id')
    context = {
        "po": po,
        "po_logs": po_log
    }
    return render(request, 'purchase_order/view_po.html', context)


@role_required('Purchase Order Edit')
def editpo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    if request.method == "POST":
        if 'addMore' in request.POST:
            form = POEditForm()
            if request.POST['product_name'] == "":
                messages.error(request, "Please select a Product!")
                return render(request, 'edit_po.html', {"po": po, "form": form})
            product = request.POST.get('product_name')
            name = inst_Product(product)
            quantity = request.POST.get('product_qty')
            supplier = po[0].supplier_name
            po_id = po[0].po_id
            poname = request.POST.get('poname')
            new = PurchaseOrder(
                po_name=poname, product_name=name, product_qty=quantity, supplier_name=supplier, po_id=po_id)
            new.save()
            return render(request, 'edit_po.html', {"po": po, "form": form})

        count = 1
        for item in po:
            item.po_name = request.POST.get('poname')
            item.product_qty = request.POST.get(f'prodqty{count}')
            item.save()
            count += 1
        return redirect('wayrem_admin:polist')
    else:
        form = POEditForm()
    return render(request, 'edit_po.html', {"po": po, "form": form})


def delete_in_edit(request, id):
    po = PurchaseOrder.objects.filter(id=id).first()
    po.delete()
    return redirect("wayrem_admin:polist")


@role_required('Purchase Order Edit')
def statuspo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    if request.method == "POST":
        status = request.POST.get('status')
        po.update(status=status)
        return redirect('wayrem_admin:polist')
    return redirect('wayrem_admin:polist')


def po_pdf(request):
    id = request.GET.get('po_id')
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'inline; attachment; filename=po' + \
    #     str(datetime.datetime.now())+'.pdf'
    # response['Content-Transfer-Encoding'] = 'binary'
    wayrem_vat = Settings.objects.filter(key="wayrem_vat").first()
    wayrem_vat = wayrem_vat.value
    po = PurchaseOrder.objects.filter(po_id=id, available=True).all()
    vat = Settings.objects.filter(key="setting_vat").first()
    vat = vat.value
    net_value = []
    vat_amt = []
    net_amt = []
    for item in po:
        total_amt = float(item.supplier_product.price)*float(item.product_qty)
        vat_float = (total_amt/100) * float(vat)
        net = total_amt+vat_float
        net_value.append(total_amt)
        vat_amt.append(vat_float)
        net_amt.append(net)
    delivery_date = (po[0].created_at + datetime.timedelta(days=5))
    context = {
        'wayrem_vat': wayrem_vat,
        'delivery_on': delivery_date,
        'data': po,
        'vat': vat,
        'total_items': len(po),
        'total_net': "{:.2f}".format(sum(net_value)),
        'total_vat': "{:.2f}".format(sum(vat_amt)),
        'total_net_amt': "{:.2f}".format(sum(net_amt))
    }
    filename = str(datetime.datetime.now())+".pdf"
    html_template = render_to_string('pdf_po/po_customer.html', context)
    pdf_file = HTML(string=html_template,
                    base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = 'inline; attachment;filename='+filename
    return response
    # html_string = render_to_string('pdf_po/po_customer.html', context)
    # html = HTML(string=html_string,
    #             base_url=request.build_absolute_uri()).render()

    # result = html.write_pdf()

    # with tempfile.NamedTemporaryFile(delete=True) as output:
    #     output.write(result)
    #     output.flush()
    #     output = open(output.name, 'rb')
    #     response.write(output.read())
    # return response


def load_supplier_products(request):
    supplier = request.GET.get('supplier')
    products = SupplierProducts.objects.filter(supplier_id=supplier)
    return render(request, 'po_supplier_products.html', {'products': products})


def confirm_delivery(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id, available=True)
    Inventory().po_inventory_process(id)
    po_name = po[0].po_name
    po_log = PO_log(po=po_name, status="confirm delivered")
    po_log.save()
    return redirect('wayrem_admin:viewpo', id)
