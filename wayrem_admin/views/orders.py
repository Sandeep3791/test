import base64
from io import BytesIO
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
from wayrem_admin.models import Orders, OrderDetails, StatusMaster, OrderDeliveryLogs, OrderTransactions
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
