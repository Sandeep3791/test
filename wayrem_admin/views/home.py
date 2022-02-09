from tracemalloc import start
from wayrem_admin.models import Customer, Notification, User, Supplier, Products, PurchaseOrder
from wayrem_admin.models_orders import OrderTransactions, Orders
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import RedirectView
from django.urls import reverse
import datetime
from django.db.models import Sum
from django.db.models.functions import (
    TruncDate, TruncDay, TruncHour, TruncMinute, TruncSecond, TruncWeek)
from django.db.models import Count


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
    subadmins = User.objects.exclude(is_superuser=True).count()
    suppliers = Supplier.objects.count()
    products = Products.objects.count()
    active_po = PurchaseOrder.objects.exclude(status="accept").count()
    completed_po = PurchaseOrder.objects.filter(status="delivered")
    sum_completed_po = sum([int(item.supplier_product.price)
                           for item in completed_po])
    customers = Customer.objects.count()
    this_month = datetime.datetime.now().month
    present_month = datetime.datetime.now()
    try:
        next_month = present_month.replace(month=present_month.month+1)
    except ValueError:
        if present_month.month == 12:
            next_month = present_month.replace(
                year=present_month.year+1, month=1)
        else:
            # next month is too short to have "same date"
            # pick your own heuristic, or re-raise the exception:
            raise
    transactions = OrderTransactions.objects.filter(
        payment_status__id=7, created_at__month=this_month)
    if transactions:
        total_transaction_amount = transactions.aggregate(
            Sum('order__grand_total'))
        total_transaction_amount = total_transaction_amount.get(
            "order__grand_total__sum")
    else:
        total_transaction_amount = 0
    # x = Orders.objects.annotate(week=TruncWeek('order_date'),day=TruncDay('order_date')).values('week','day').annotate(total=Count('id'))
    #  x = Orders.objects.annotate(week=TruncWeek('order_date')).values('week').annotate(total=Count('id'))
    context = {
        'subadmins': subadmins,
        'suppliers': suppliers,
        'products': products,
        'customers': customers,
        'active_po': active_po,
        'completed_po': len(completed_po),
        'sum_completed_po': sum_completed_po,
        'transactions': len(transactions),
        'total_transaction_amount': total_transaction_amount,
        'present_month': present_month.strftime("%b"),
        'next_month': next_month.strftime("%b")
    }
    return render(request, 'dashboard.html', context)


def notification_delete(request, id):
    notify = Notification.objects.filter(id=id).first()
    a = notify.message
    po_no = list(filter(lambda word: word[0:3] == 'PO/', a.split()))[0]
    po = PurchaseOrder.objects.filter(po_name=po_no).first()
    po_id = po.po_id
    notify.delete()
    return redirect('wayrem_admin:viewpo', po_id)
