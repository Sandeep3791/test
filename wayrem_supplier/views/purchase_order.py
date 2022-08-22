from django.db import connection
import constant
from django.core.checks import messages
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from wayrem_supplier.models import Invoice, PO_log, PurchaseOrder, Notification, Supplier, Settings, EmailTemplateModel
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_supplier.export import generate_excel
from wayrem_supplier.export import generate_excel
from django.contrib import messages
import json
import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
import threading
from wayrem_supplier.services import send_email


class PurchaseOrderList(View):
    template_name = "purchaseorderlist.html"

    # @method_decorator(login_required(login_url='/'))
    def get(self, request, format=None):
        if request.session.get('supplier') is None:
            return redirect('wayrem_supplier:login')
        # supplier_id = SupplierRegister.objects.filter(id= id).first()
        supplier_id = request.session.get("supplier_id")
        print(type(supplier_id))
        cholist = PurchaseOrder.objects.filter(supplier_name=supplier_id).values(
            'po_id', 'po_name', 'status',).distinct().order_by('-created_at')
        # cholist = list(data.values('po_id', 'po_name',
        #                'created_at', 'status').distinct())
        paginator = Paginator(cholist, 25)
        page = request.GET.get('page')
        try:
            cholist = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            cholist = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            cholist = paginator.page(paginator.num_pages)
            print(cholist)
        return render(request, 'purchaseorderlist.html', {'cholist': cholist})


def po_details(request, id=None):
    if request.session.get('supplier') is None:
        return redirect('wayrem_supplier:login')
    po = PurchaseOrder.objects.filter(po_id=id).exclude(available=False)
    # polist = list(po.values())
    poname = po[0].po_name
    polog = PO_log.objects.filter(po=poname).order_by('id')
    invo = Invoice.objects.filter(po_name=poname)
    return render(request, 'po_details.html', {"polist": po, 'id': id, 'invo': invo, 'polog': polog})


def po_details_invoice(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    # polist = list(po.values())
    return render(request, 'po_details_invoice.html', {"polist": po})


def statuspo(request, id=None):
    po = PurchaseOrder.objects.filter(po_id=id).all()
    if request.method == "POST":
        products = [int(v) for k, v in request.POST.items()
                    if k.startswith('available')]
        if len(products) == 0:
            messages.error(request, "Can't approve without product!S")
            return redirect('wayrem_supplier:podetails', id)
        x = [z.id for z in po]
        unavailable_products = [i.product_name.name for i in po]
        new_list = list(set(x).difference(products))
        for i in new_list:
            availability = PurchaseOrder.objects.filter(id=i).first()
            availability.available = False
            availability.save()
            print("Done")

        po.update(status="approved")
        v = po[0].po_name
        logs = PO_log(po=v, status='approved')
        logs.save()
        supplier_name = Supplier.objects.filter(
            username=request.session.get('supplier')).first()
        email_template = get_object_or_404(EmailTemplateModel, key="po_accept")
        subject = email_template.subject.format(po_number=v)
        body = email_template.message_format
        values = {
            'supplier': supplier_name.company_name,
            'po_number': v,
        }
        body = body.format(**values)
        emails = None
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT email FROM {constant.database}.users_master where is_superuser=True or role_id in (SELECT role_id FROM {constant.database}.role_permissions where function_id = (SELECT id FROM {constant.database}.function_master where codename = 'purchase_orders.notifications'));")
            y = constant.dictfetchall(cursor)
            emails = [i['email'] for i in y]
        if emails:
            for to in emails:
                t = threading.Thread(
                    target=send_email, args=(to, subject, body))
                t.start()
        setting = Settings.objects.filter(key="po_approve").first()
        message = setting.value
        msg = message.format(number=po[0].po_name,
                             supplier=supplier_name.company_name)
        notify = Notification(
            message=msg, status=True, supplier=supplier_name)
        notify.save()
    return redirect('wayrem_supplier:podetails', id)


def po_excel(request):
    return generate_excel("po_master", "po")


def deny_comment(request, id=None):
    deny_comment_box = request.POST.get('deny_comment_box')
    po = PurchaseOrder.objects.filter(po_id=id).all()
    status = "declined"
    po.update(status=status, reason=deny_comment_box)
    po_name = po[0].po_name
    supplier_id = request.session.get('supplier_id')
    supplier = Supplier.objects.filter(id=supplier_id).first()
    email_template = get_object_or_404(EmailTemplateModel, key="po_reject")
    subject = email_template.subject.format(po_number=po_name)
    body = email_template.message_format
    values = {
        'supplier': supplier.company_name,
        'po_number': po_name,
        'reason': deny_comment_box
    }
    body = body.format(**values)
    emails = None
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT email FROM {constant.database}.users_master where is_superuser=True or role_id in (SELECT role_id FROM {constant.database}.role_permissions where function_id = (SELECT id FROM {constant.database}.function_master where codename = 'purchase_orders.notifications'));")
        y = constant.dictfetchall(cursor)
        emails = [i['email'] for i in y]
    if emails:
        for to in emails:
            t = threading.Thread(
                target=send_email, args=(to, subject, body))
            t.start()
    setting = Settings.objects.filter(key="po_declined").first()
    message = setting.value
    msg = message.format(
        number=po[0].po_name, supplier=supplier.company_name, reason=deny_comment_box)
    notify = Notification(
        message=msg, status=True, supplier=supplier)
    notify.save()
    return redirect('wayrem_supplier:purchase_order_list')


def delivered_status(request):
    id = request.GET.get('id')
    po = PurchaseOrder.objects.filter(po_id=id).all()
    dstatus = request.GET.get('d_status')
    # status = "delivered"
    po.update(status=dstatus)
    v = po[0].po_name
    logs = PO_log(po=v, status=dstatus)
    logs.save()
    supplier_id = request.session.get('supplier_id')
    supplier = Supplier.objects.filter(id=supplier_id).first()
    if 'preparing order' in dstatus:
        setting = Settings.objects.filter(key="po_prepare").first()
    elif 'shipping order' in dstatus:
        setting = Settings.objects.filter(key="po_shipping").first()
    elif 'delivered' in dstatus:
        setting = Settings.objects.filter(key="po_delivered").first()
    email_template = get_object_or_404(
        EmailTemplateModel, key="po_delivery_status")
    subject = email_template.subject.format(po_number=v, status=dstatus)
    body = email_template.message_format
    values = {
        'supplier': supplier.company_name,
        'po_number': v,
        'status': dstatus
    }
    body = body.format(**values)
    emails = None
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT email FROM {constant.database}.users_master where is_superuser=True or role_id in (SELECT role_id FROM {constant.database}.role_permissions where function_id = (SELECT id FROM {constant.database}.function_master where codename = 'purchase_orders.notifications'));")
        y = constant.dictfetchall(cursor)
        emails = [i['email'] for i in y]
    if emails:
        for to in emails:
            t = threading.Thread(
                target=send_email, args=(to, subject, body))
            t.start()
    message = setting.value
    msg = message.format(number=po[0].po_name, supplier=supplier.company_name)
    notify = Notification(
        message=msg, status=True, supplier=supplier)
    notify.save()
    return redirect('wayrem_supplier:purchase_order_list')


# def po_log_details(request, id=None):
#     po = PurchaseOrder.objects.filter(po_id=id).all()
#     poname = po[0].po_name
#     polog = PO_log.objects.filter(po=poname).order_by('id')

#     data = json.dumps({
#         'id': id,
#         'polog':polog,
#     })
#     return HttpResponse(data, content_type='application/json')us


def invoice_status(request):
    po_name = request.GET.get('invoice_no')
    try:
        invoice_po = Invoice.objects.filter(po_name=po_name).first()
        if invoice_po:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    except:
        return HttpResponse(False)


# def po_pdf(request):
#     id = request.GET.get('po_id')
#     wayrem_vat = Settings.objects.filter(key="wayrem_vat").first()
#     wayrem_vat = wayrem_vat.value
#     po = PurchaseOrder.objects.filter(po_id=id, available=True).all()
#     vat = Settings.objects.filter(key="setting_vat").first()
#     vat = vat.value
#     net_value = []
#     vat_amt = []
#     net_amt = []
#     for item in po:
#         total_amt = float(item.supplier_product.price)*float(item.product_qty)
#         vat_float = (total_amt/100) * float(vat)
#         net = total_amt+vat_float
#         net_value.append(total_amt)
#         vat_amt.append(vat_float)
#         net_amt.append(net)
#     delivery_date = (po[0].created_at + datetime.timedelta(days=5))
#     context = {
#         'wayrem_vat': wayrem_vat,
#         'delivery_on': delivery_date,
#         'data': po,
#         'vat': vat,
#         'total_items': len(po),
#         'total_net': "{:.2f}".format(sum(net_value)),
#         'total_vat': "{:.2f}".format(sum(vat_amt)),
#         'total_net_amt': "{:.2f}".format(sum(net_amt))
#     }
#     filename = str(datetime.datetime.now())+".pdf"
#     html_template = render_to_string('po_customer_supplier.html', context)
#     pdf_file = HTML(string=html_template,
#                     base_url=request.build_absolute_uri()).write_pdf()
#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Transfer-Encoding'] = 'binary'
#     response['Content-Disposition'] = 'inline; attachment;filename='+filename
#     return response


def po_pdf(request):
    id = request.GET.get('po_id')
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'inline; attachment; filename=po' + \
    #     str(datetime.datetime.now())+'.pdf'
    # response['Content-Transfer-Encoding'] = 'binary'
    wayrem_vat = Settings.objects.filter(key="wayrem_vat").first()
    wayrem_vat = wayrem_vat.value
    po = PurchaseOrder.objects.filter(po_id=id, available=True).all()
    vat_no = Settings.objects.filter(key="wayrem_vat_registration").first()
    cr_no = Settings.objects.filter(key="wayrem_cr_no").first()
    net_value = []
    vat_amt = []
    net_amt = []
    for item in po:
        total_amt = float(item.supplier_product.price)*float(item.product_qty)
        vat_float = (total_amt/100) * float(wayrem_vat)
        net = total_amt+vat_float
        net_value.append(total_amt)
        vat_amt.append(vat_float)
        net_amt.append(net)
    try:
        po_log = PO_log.objects.filter(
            po=po[0].po_name, status="confirm delivered").first()
        delivery_date = po_log.created_at
    except:
        delivery_date = po[0].updated_at
    context = {
        'delivery_on': delivery_date,
        'data': po,
        'vat_no': vat_no.value,
        'cr_no': cr_no.value,
        'vat': wayrem_vat,
        'total_items': len(po),
        'total_net': "{:.2f}".format(sum(net_value)),
        'total_vat': "{:.2f}".format(sum(vat_amt)),
        'total_net_amt': "{:.2f}".format(sum(net_amt))
    }
    filename = str(datetime.datetime.now())+".pdf"
    html_template = render_to_string('po_customer_supplier.html', context)
    pdf_file = HTML(string=html_template,
                    base_url=request.build_absolute_uri()).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = 'inline; attachment;filename='+filename
    return response
