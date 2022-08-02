import base64
from io import BytesIO
from itertools import product
from unittest import result
import qrcode
from fatoora import Fatoora
from django.shortcuts import render, redirect
from django.contrib import messages

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from wayrem_admin.models import Settings
from wayrem_admin.forms import SettingsForm
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wayrem_admin.export import generate_excel
from wayrem_admin.models import Orders, OrderDetails, StatusMaster, OrderDeliveryLogs, OrderTransactions,create_new_ref_number
from wayrem_admin.models import Inventory
from wayrem_admin.models import Settings
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView
from wayrem_admin.forms import OrderStatusUpdatedForm, OrderAdvanceFilterForm, OrderStatusDetailForm, OrderUpdatedPaymentStatusForm, OrderStatusFilter
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from wayrem_admin.utils.constants import *
from wayrem_admin.filters.order_filters import OrderFilter
from django.db.models import Sum, Case, CharField, Value, When
from django.db.models import F
import datetime
import xlsxwriter
import io
# pdf export
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from wayrem_admin.loginext.loginext_liberary import LoginextOrderCreate
import json

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from wayrem_admin.permissions.mixins import LoginPermissionCheckMixin
import threading
from wayrem_admin.models import Products
from django.db.models import Q
from wayrem_admin.forecasts.order_liberary import OrderLiberary
from datetime import timedelta, date, datetime
from wayrem_admin.views.credits import credit_refund

@method_decorator(csrf_exempt, name='dispatch')
class OrderReferenceExport(View):
    model = Orders
    template_name = "orders/order_invoice.html"
    KEY = 'setting_vat'
    WAYREM_VAT = 'wayrem_vat_registration'
    WAYREM_CR = 'wayrem_cr_no'

    def image_to_base64(self, image):
        buff = BytesIO()
        image.save(buff, format="png")
        img_str = base64.b64encode(buff.getvalue())
        return img_str.decode("utf-8")

    def get(self, request, id):
        context = {}
        context['currency'] = CURRENCY
        order_id = Orders.objects.filter(ref_number=id).first()
        if order_id is None:
            return 1
        else:
            order_ids = order_id.id

        order_id = order_ids
        orders_details = Orders.objects.filter(id=order_id).first()
        filename = "order-"+str(orders_details.ref_number)+".pdf"
        context['order'] = orders_details
        context['tax_vat'] = Settings.objects.filter(key=self.KEY).first()
        context['wayrem_vat'] = Settings.objects.filter(
            key=self.WAYREM_VAT).first()
        context['wayrem_cr'] = Settings.objects.filter(
            key=self.WAYREM_CR).first()
        context['wayrem_seller_name'] = Settings.objects.filter(
            key="wayrem_seller_name").first()
        context['order_details'] = OrderDetails.objects.filter(order=order_id)
        context['order_transaction'] = OrderTransactions.objects.filter(
            order=order_id).first()
        fatoora_obj = Fatoora(
            seller_name=context['wayrem_seller_name'].value,
            tax_number=context['wayrem_vat'].value,
            # invoice_date="2021-07-12T14:25:09+00:00",
            invoice_date=orders_details.order_date,
            total_amount=orders_details.grand_total,
            tax_amount=orders_details.tax,
        )
        qr_code = qrcode.make(fatoora_obj.base64)
        image = self.image_to_base64(qr_code)
        context['image'] = image
        html_template = render_to_string(self.template_name, context)
        pdf_file = HTML(string=html_template,
                        base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Transfer-Encoding'] = 'binary'
        response['Content-Disposition'] = 'attachment;filename='+filename
        return response


class OrderExportView(View):

    @method_decorator(login_required(login_url='wayrem_admin:root'))
    def get(self, request, **kwargs):
        qs = Orders.objects.annotate(OrderReference=F('ref_number'), OrderDate=F('order_date'), Customer=F('customer__first_name'), Mobile=F('order_phone'), Status=F(
            'status__name'), Items=Value('', output_field=CharField()), Total=F('grand_total')).values('id', 'OrderReference', 'OrderDate', 'Customer', 'Mobile', 'Status', 'Items', 'Total')
        filtered_list = OrderFilter(self.request.GET, queryset=qs)
        query_set = filtered_list.qs
        for qs_field in query_set:
            qs_field['Items'] = OrderDetails.objects.filter(
                order=qs_field['id']).count()
            qs_field['OrderDate'] = qs_field['OrderDate'].strftime("%d %b %Y")
            del qs_field['id']
        response = self.genrate_excel(query_set)
        return response

    def genrate_excel(self, query_set):
        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        for row_number, query in enumerate(query_set):
            col_key = 0
            for key, values in query.items():
                if row_number == 0:
                    bold = workbook.add_format(
                        {'bold': True, 'font_color': 'white', 'bg_color': '#0d72ba'})
                    worksheet.set_row(row_number, 30)
                    worksheet.write(row_number, col_key, key, bold)
                    worksheet.set_column(row_number, col_key, 20)
                worksheet.write(row_number+1, col_key, values)
                col_key = col_key+1

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)
        filename = 'order_report.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


class OrdersList(LoginPermissionCheckMixin, ListView):
    permission_required = 'order.list_view'
    login_url = 'wayrem_admin:root'
    model = Orders
    template_name = "orders/list.html"
    context_object_name = 'orders'
    paginate_by = RECORDS_PER_PAGE
    success_url = reverse_lazy('wayrem_admin:orderlist')

    def get_queryset(self):
        qs = Orders.objects.filter(is_shown=1).order_by("-id")
        filtered_list = OrderFilter(self.request.GET, queryset=qs)
        print(filtered_list.qs.query)
        return filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(OrdersList, self).get_context_data(**kwargs)
        context['filter_form'] = OrderAdvanceFilterForm(self.request.GET)
        context['status_filter_form'] = OrderStatusFilter(self.request.GET)
        return context


class OrderStatusUpdated(LoginRequiredMixin, UpdateView):
    login_url = 'wayrem_admin:root'
    model = Orders
    form_class = OrderStatusUpdatedForm
    template_name = "orders/update_order_status.html"
    pk_url_kwarg = 'id'

    def dispatch(self, *args, **kwargs):
        return super(OrderStatusUpdated, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_pk = self.kwargs['id']
        context['id_pk'] = id_pk
        order_transaction = OrderTransactions.objects.filter(
            order_id=id_pk).first()
        if (order_transaction.payment_mode_id == BANKTRANSFER_MODE) and (order_transaction.payment_status_id == PAYMENT_STATUS_PENDING_APPROVAL or order_transaction.payment_status_id == PAYMENT_STATUS_PENDING or order_transaction.payment_status_id == PAYMENT_STATUS_DECLINED or order_transaction.payment_status_id == PAYMENT_STATUS_REJECTED):
            context['message'] = "Please confirm the Bank Transfer document before approving the order"
        else:
            context['message'] = ""
        return context

    def loginext_api(self, order_id, status_id):
        loginext_status = None
        if status_id == ORDER_APPROVED:
            ordercreate = LoginextOrderCreate()
            loginext_status = ordercreate.ordercreate(order_id)
        return loginext_status

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        obj = form.save(commit=False)
        status_id = int(self.request.POST.get('status'))
        obj.status = StatusMaster.objects.get(id=status_id)
        print(status_id)
        print("ka")
        obj.save()
        return HttpResponse(True)

    def post(self, request, *args, **kwargs):
        get_id = self.get_object().id
        exist_status_id = self.get_object().status.id
        status_id = int(self.request.POST.get('status'))
        
        data_dic = {}
        data_dic['status'] = 0
        data_dic['loginext_success'] = None
        data_dic['order_status'] = None
        data_dic['delivery_status'] = None
        data_dic['message'] = ''

        
        if exist_status_id != status_id:
            log_status = self.loginext_api(get_id, status_id)
            data_dic['status'] = 1

            if status_id == ORDER_APPROVED:
                delivery_status = ORDER_STATUS_PREPARING
            if status_id == ORDER_CANCELLED:
                delivery_status = ORDER_STATUS_CANCELLED
                payment_status = StatusMaster.objects.get(
                    id=PAYMENT_STATUS_DECLINED)

            obj_stat_instance = StatusMaster.objects.get(id=status_id)


            if status_id == ORDER_CANCELLED:
                order_transaction=OrderTransactions.objects.filter(order=get_id).first()
                if order_transaction.payment_mode.id == CREDIT_MODE:
                    credit_refund(get_id) # get id == order id 

            if status_id == ORDER_CANCELLED:
                OrderTransactions.objects.filter(order=get_id).update(
                    payment_status=payment_status)
                if obj_stat_instance.id == ORDER_CANCELLED:
                    t = threading.Thread(
                        target=self.order_notification_customer, args=(get_id, ORDER_CANCELLED,))
                    t.start()
            deliv_obj_stat_instance = StatusMaster.objects.get(
                id=delivery_status)
            now = datetime.datetime.now()
            if log_status:
                data_dic['loginext_success'] = 1
                if log_status == 2:
                    data_dic['message'] = "Reference Id already created. We update the status"
                else:
                    data_dic['message'] = "Reference Id is created. We update the status"
                    if status_id == ORDER_APPROVED:
                        t = threading.Thread(
                            target=self.order_notification_customer, args=(get_id, ORDER_APPROVED,))
                        t.start()
                Orders.objects.filter(id=get_id).update(
                    status=obj_stat_instance, delivery_status=deliv_obj_stat_instance)
                odl = OrderDeliveryLogs(order_id=get_id, order_status=deliv_obj_stat_instance, order_status_details="status change",
                                        log_date=now, user_id=1, customer_view=deliv_obj_stat_instance.customer_view)

                odl.save()

                data_dic['order_status'] = '<span class="badge bg-primary" style="padding: 3px 8px;line-height: 11px;background-color:' + \
                    obj_stat_instance.status_color+' !important">'+obj_stat_instance.name+'</span>'
                data_dic['delivery_status'] = '<span class="badge bg-primary" style="padding: 3px 8px;line-height: 11px;background-color:' + \
                    deliv_obj_stat_instance.status_color+' !important">' + \
                    deliv_obj_stat_instance.name+'</span>'
            else:
                data_dic['loginext_success'] = 0
                data_dic['message'] = "Reference Id is not created. Please check the order."

            if log_status is None:
                data_dic['loginext_success'] = None
                Orders.objects.filter(id=get_id).update(
                    status=obj_stat_instance, delivery_status=deliv_obj_stat_instance)
                odl = OrderDeliveryLogs(order_id=get_id, order_status=deliv_obj_stat_instance, order_status_details="status change",
                                        log_date=now, user_id=1, customer_view=deliv_obj_stat_instance.customer_view)
                odl.save()
                data_dic['message'] = "Status Updated"
                data_dic['order_status'] = '<span class="badge bg-primary" style="padding: 3px 8px;line-height: 11px;background-color:' + \
                    obj_stat_instance.status_color+' !important">'+obj_stat_instance.name+'</span>'
                data_dic['delivery_status'] = '<span class="badge bg-primary" style="padding: 3px 8px;line-height: 11px;background-color:' + \
                    deliv_obj_stat_instance.status_color+' !important">' + \
                    deliv_obj_stat_instance.name+'</span>'
        else:
            data_dic['message'] = 'Same status not updated.'

        data_dic_json = json.dumps(data_dic)
        return HttpResponse(data_dic_json)

    def order_notification_customer(self, order_id, status_id):
        from wayrem_admin.forecasts.firebase_notify import FirebaseLibrary
        FirebaseLibrary().send_notify(order_id=order_id, order_status=status_id)
        return 1


class OrderPaymentStatusUpdated(LoginRequiredMixin, UpdateView):
    login_url = 'wayrem_admin:root'
    model = OrderTransactions
    form_class = OrderUpdatedPaymentStatusForm
    template_name = "orders/update_order_status.html"
    pk_url_kwarg = 'id'

    def dispatch(self, *args, **kwargs):
        return super(OrderPaymentStatusUpdated, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        get_id = self.get_object().id
        order_trans = OrderTransactions.objects.get(id=get_id)
        order_id = order_trans.order_id
        order_payment_mode = order_trans.payment_mode_id
        status_id = int(self.request.POST.get('payment_status'))
        obj_stat_instance = StatusMaster.objects.get(id=status_id)
        OrderTransactions.objects.filter(id=get_id).update(
            payment_status=obj_stat_instance)
        t = threading.Thread(target=self.payment_notification_send, args=(
            order_id, status_id, order_payment_mode,))
        t.start()
        return HttpResponse(obj_stat_instance.name)

    def payment_notification_send(self, order_id, status_id, order_payment_mode):
        if order_payment_mode == BANKTRANSFER_MODE:
            from wayrem_admin.forecasts.firebase_notify import FirebaseLibrary
            if status_id == PAYMENT_STATUS_REJECTED:
                FirebaseLibrary().send_notify(order_id=order_id,order_status=PAYMENT_STATUS_REJECTED)
            elif status_id == PAYMENT_STATUS_CONFIRM:
                FirebaseLibrary().send_notify(order_id=order_id, order_status=PAYMENT_STATUS_CONFIRM)
        return 1


class OrderInvoiceView(LoginRequiredMixin, View):
    login_url = 'wayrem_admin:root'
    model = Orders
    template_name = "orders/order_invoice.html"
    KEY = 'setting_vat'
    WAYREM_VAT = 'wayrem_vat_registration'
    WAYREM_CR = 'wayrem_cr_no'

    def image_to_base64(self, image):
        buff = BytesIO()
        image.save(buff, format="png")
        img_str = base64.b64encode(buff.getvalue())
        return img_str.decode("utf-8")

    def get(self, request, id):
        context = {}
        context['currency'] = CURRENCY
        order_id = id
        orders_details = Orders.objects.filter(id=order_id).first()
        filename = "order-"+str(orders_details.ref_number)+".pdf"
        context['order'] = orders_details
        context['tax_vat'] = Settings.objects.filter(key=self.KEY).first()
        context['wayrem_vat'] = Settings.objects.filter(
            key=self.WAYREM_VAT).first()
        context['wayrem_cr'] = Settings.objects.filter(
            key=self.WAYREM_CR).first()
        context['wayrem_seller_name'] = Settings.objects.filter(
            key="wayrem_seller_name").first()
        context['order_details'] = OrderDetails.objects.filter(order=order_id)
        context['order_transaction'] = OrderTransactions.objects.filter(
            order=order_id).first()
        fatoora_obj = Fatoora(
            seller_name=context['wayrem_seller_name'].value,
            tax_number=context['wayrem_vat'].value,
            # invoice_date="2021-07-12T14:25:09+00:00",
            invoice_date=orders_details.order_date,
            total_amount=orders_details.grand_total,
            tax_amount=orders_details.tax,
        )
        qr_code = qrcode.make(fatoora_obj.base64)
        image = self.image_to_base64(qr_code)
        context['image'] = image
        html_template = render_to_string(self.template_name, context)
        pdf_file = HTML(string=html_template,
                        base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Transfer-Encoding'] = 'binary'
        response['Content-Disposition'] = 'inline;attachment;filename='+filename
        return response
        # return render(request, self.template_name,context)


class OrderUpdateView(LoginPermissionCheckMixin, DetailView):
    permission_required = 'order.view_order'
    login_url = 'wayrem_admin:root'
    model = Orders
    template_name = "orders/order_page.html"
    context_object_name = 'order'
    KEY = 'setting_vat'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.get_object().id
        
        context['order_details'] = OrderDetails.objects.filter(order=order_id)
        context['tax_vat'] = Settings.objects.filter(key=self.KEY).first()
        context['order_timeline'] = OrderDeliveryLogs.objects.filter(
            order=order_id).order_by('id')
        context['order_transaction'] = OrderTransactions.objects.filter(
            order=order_id).first()
        duplicaterequest = []
        duplicaterequest = self.request.GET.copy()
        duplicaterequest['status'] = self.get_object().status.id
        duplicaterequest['payment_status'] = context['order_transaction'].payment_status.id
        context['status_form'] = OrderStatusDetailForm(
            self.get_object().status.id, order_id, duplicaterequest)
        context['payment_status_form'] = OrderUpdatedPaymentStatusForm(
            duplicaterequest)
        context['currency'] = CURRENCY
        context['PAYMENT_STATUS_CONFIRM'] = PAYMENT_STATUS_CONFIRM
        context['PAYMENT_STATUS_DECLINED'] = PAYMENT_STATUS_DECLINED
        context['PAYMENT_STATUS_REJECTED'] = PAYMENT_STATUS_REJECTED
        order_transaction = OrderTransactions.objects.filter(
            order_id=order_id).first()
        if (order_transaction.payment_mode_id == BANKTRANSFER_MODE) and (order_transaction.payment_status_id == PAYMENT_STATUS_PENDING_APPROVAL or order_transaction.payment_status_id == PAYMENT_STATUS_PENDING or order_transaction.payment_status_id == PAYMENT_STATUS_DECLINED or order_transaction.payment_status_id == PAYMENT_STATUS_REJECTED):
            context['message'] = "Please confirm the Bank Transfer document before approving the order"
        else:
            context['message'] = ""
        return context

class OrderCancelCloneOrder(View):
    model = Orders
    def get(self, request, id):
        context = {}
        from datetime import datetime
        new_order=self.model.objects.filter(id=id).values().first() 
        new_ref_number = create_new_ref_number()
        new_order.update({'id': None,'ref_number':new_ref_number,'from_clone':id})
        new_order_created = self.model.objects.create(**new_order)
        new_order_id=new_order_created.id
        orderdetail=OrderDetails.objects.filter(order_id=id).values()
        for od in orderdetail:
            od.update({'id':None,'order_id':new_order_id})
            OrderDetails.objects.create(**od)
        self.model.objects.filter(id=id).update(to_clone=new_order_id)
        new_order_transaction=OrderTransactions.objects.filter(order_id =id).values().first()
        new_order_transaction.update({'id': None,'order_id':new_order_id})
        OrderTransactions.objects.create(**new_order_transaction)

        neworderlog=OrderDeliveryLogs.objects.filter(order_id=id,order_status=1).values().first()
        if neworderlog is not None:
            neworderlog.update({'id':None,'order_id':new_order_id,'log_date':datetime.now()})
            OrderDeliveryLogs.objects.create(**neworderlog)
        return redirect('wayrem_admin:cloneorder', pk=new_order_id)

class CloneOrderView(DetailView):
    model = Orders
    template_name = "orders/orderclone/order_clone.html"
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product']=None
        order_id = self.get_object().id
        from_clone_id=Orders.objects.filter(id=order_id).values('from_clone').first()
        
        order_transaction=OrderTransactions.objects.filter(order_id=from_clone_id['from_clone']).first()
        
        context['order_invoice'] =order_transaction.invoices_id
        context['order_ref'] =order_transaction.order.ref_number 
        pid=self.request.GET.get('pid')
        if pid != "":
            products=Products.objects.filter(id=pid).first()
            if products is not None:
                context['product']=products

        context['pid'] =pid     
        context['order_details'] = OrderDetails.objects.filter(order=order_id)
        context['currency'] = CURRENCY
        return context

class InsertOrderdetail(View):
    model = Orders
    def post(self, request,id,pid):
        quantity=self.request.POST.get('quantity')
        order_detail=OrderDetails.objects.filter(order_id=id,product_id=pid).values().first()
        product=Products.objects.filter(id=pid).first()
        if order_detail is None:
            od_det_dic=OrderLiberary().create_product(id,quantity, product)
        else:
            cur_qty=order_detail['quantity']
            total_qty=int(cur_qty)+int(quantity)
            od_det_dic=OrderLiberary().create_product(id,total_qty, product)
            od_det_dic.update({'id':order_detail['id']})
        od = OrderDetails(**od_det_dic)
        od.save()

        order_dic=self.update_order(id)
        return redirect('wayrem_admin:cloneorder', pk=id)

    def update_order(self,order_id):
        order=Orders.objects.filter(id=order_id).first()
        tax_vat = OrderLiberary().get_tax_vat()
        product_total = self.calculate_price(order_id)
        sub_total = round(product_total['sub_total'], 2)
        item_margin = round(product_total['item_margin'], 2)
        total = round(product_total['total'], 2)        
        order_lat=order.order_ship_latitude
        order_long = order.order_ship_longitude
        shipping = OrderLiberary().get_shipping_value(total,order_lat,order_long)
        item_discount = round(product_total['item_discount'], 2)
        discount = round(product_total['discount'], 2)
        grand_total, tax = OrderLiberary().get_grand_total(total, tax_vat, shipping)
        currentTimeDate = datetime.now() + timedelta(days=1)
        order_date = currentTimeDate
        order_dic = {'sub_total': sub_total, 'item_discount': item_discount, 'item_margin': item_margin, 'tax': tax, 'tax_vat': tax_vat, 'shipping': shipping, 'total': total, 'discount': discount, 'grand_total': grand_total,'order_date': order_date}
        Orders.objects.filter(id=order_id).update(**order_dic)
        return 1

    def calculate_price(self,order_id):
        order_detail_list=OrderDetails.objects.filter(order_id=order_id)
        subtotal_unit_price = 0
        product_total = {}
        total_item_discount = 0
        total_item_margin = 0
        for gpl in order_detail_list:
            quantity = float(gpl.quantity)
            if quantity:
                product_subtotal = float(gpl.product.price)
                product_margin_amount = OrderLiberary().calculate_price_unit_type(
                    gpl.product.wayrem_margin, gpl.product.price, gpl.product.margin_unit)
                if gpl.product.discount is None:
                    product_discount_price = 0
                    total_price_margin = product_subtotal+product_margin_amount
                else:
                    product_discount_price = gpl.product.discount
                    total_price_margin = product_subtotal+product_margin_amount
                total_product_discount_price = OrderLiberary().calculate_price_unit_type(
                    product_discount_price, total_price_margin, gpl.product.dis_abs_percent)

                subtotal_unit_price += (product_subtotal+product_margin_amount -
                                        total_product_discount_price) * quantity
                total_item_discount += (total_product_discount_price * quantity)
                total_item_margin += (product_margin_amount * quantity)

        product_total = {'sub_total': subtotal_unit_price, 'item_margin': total_item_margin,
                         'total': subtotal_unit_price, 'item_discount': total_item_discount, 'discount': 0}
        return product_total

class AutoCompleteModelView(View):
    model=Orders

    def post(self,request):
        search=self.request.POST.get('search')
        pro_list=Products.objects.filter(Q(name__contains=search) | Q(SKU__contains=search)).values('id','name','SKU')
        results = []
        for pro in pro_list:
            new_dic={'value':pro['id'],'label':pro['SKU'] +" - "+pro['name']}
            results.append(new_dic)
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

class OrderRemoveDetail(View):
    model=OrderDetails
    def get(self,request):
        return HttpResponse("1")
    def post(self,request):
        order_id=self.request.POST.get('order_id')
        order_detail_id=self.request.POST.get('order_detail_id')
        OrderDetails.objects.filter(id=order_detail_id).delete()
        self.update_order(order_id)
        return HttpResponse("1")

    def update_order(self,order_id):
        order=Orders.objects.filter(id=order_id).first()
        tax_vat = OrderLiberary().get_tax_vat()
        product_total = self.calculate_price(order_id)
        sub_total = round(product_total['sub_total'], 2)
        item_margin = round(product_total['item_margin'], 2)
        total = round(product_total['total'], 2)        
        order_lat=order.order_ship_latitude
        order_long = order.order_ship_longitude
        shipping = OrderLiberary().get_shipping_value(total,order_lat,order_long)
        item_discount = round(product_total['item_discount'], 2)
        discount = round(product_total['discount'], 2)
        grand_total, tax = OrderLiberary().get_grand_total(total, tax_vat, shipping)
        currentTimeDate = datetime.now() + timedelta(days=1)
        order_date = currentTimeDate
        order_dic = {'sub_total': sub_total, 'item_discount': item_discount, 'item_margin': item_margin, 'tax': tax, 'tax_vat': tax_vat, 'shipping': shipping, 'total': total, 'discount': discount, 'grand_total': grand_total,'order_date': order_date}
        Orders.objects.filter(id=order_id).update(**order_dic)
        return 1

    def calculate_price(self,order_id):
        order_detail_list=OrderDetails.objects.filter(order_id=order_id)
        subtotal_unit_price = 0
        product_total = {}
        total_item_discount = 0
        total_item_margin = 0
        for gpl in order_detail_list:
            quantity = float(gpl.quantity)
            if quantity:
                product_subtotal = float(gpl.product.price)
                product_margin_amount = OrderLiberary().calculate_price_unit_type(
                    gpl.product.wayrem_margin, gpl.product.price, gpl.product.margin_unit)
                if gpl.product.discount is None:
                    product_discount_price = 0
                    total_price_margin = product_subtotal+product_margin_amount
                else:
                    product_discount_price = gpl.product.discount
                    total_price_margin = product_subtotal+product_margin_amount
                total_product_discount_price = OrderLiberary().calculate_price_unit_type(
                    product_discount_price, total_price_margin, gpl.product.dis_abs_percent)

                subtotal_unit_price += (product_subtotal+product_margin_amount -
                                        total_product_discount_price) * quantity
                total_item_discount += (total_product_discount_price * quantity)
                total_item_margin += (product_margin_amount * quantity)

        product_total = {'sub_total': subtotal_unit_price, 'item_margin': total_item_margin,
                         'total': subtotal_unit_price, 'item_discount': total_item_discount, 'discount': 0}
        return product_total