from tracemalloc import start
from wayrem_admin.models import Customer, Notification, User, Supplier, Products, PurchaseOrder
from wayrem_admin.models import OrderTransactions, Orders
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import RedirectView
from django.urls import reverse
import datetime
from django.db.models import Sum
from django.db.models.functions import (
    TruncDate, TruncDay, TruncHour, TruncMinute, TruncSecond, TruncWeek, TruncMonth)
from django.db.models import Count
from dateutil import relativedelta
from wayrem_admin.models.users import Users


class RootUrlView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse('wayrem_admin:login')
        return reverse('wayrem_admin:dashboard')


@ login_required(login_url='wayrem_admin:root')
def dashboard(request):
    subadmins = Users.objects.exclude(is_superuser=True).count()
    suppliers = Supplier.objects.count()
    products = Products.objects.count()
    active_po = PurchaseOrder.objects.filter(status="accept").values(
        'po_name', 'supplier_name__company_name', 'po_id', 'status').distinct().count()
    completed_po_count = PurchaseOrder.objects.filter(status="delivered").values(
        'po_name', 'supplier_name__company_name', 'po_id', 'status').distinct().count()
    completed_po = PurchaseOrder.objects.filter(status="delivered")
    sum_completed_po = sum([float(item.supplier_product.price)
                           for item in completed_po])
    this_month = datetime.datetime.now().month
    this_day = datetime.datetime.now().day
    customers_day = Customer.objects.filter(created_at__day=this_day).count()
    customers_month = Customer.objects.filter(
        created_at__month=this_month).count()
    orders_day = Orders.objects.filter(order_date__day=this_day).count()
    orders_month = Orders.objects.filter(
        order_date__month=this_month).count()
    present_month = datetime.datetime.now()
    try:
        next_month = datetime.date.today() + relativedelta.relativedelta(months=1)
        # next_month = present_month.replace(month=present_month.month+1)
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
    today = datetime.date.today()
    print(today)
    week_ago = today - datetime.timedelta(days=7)
    x = Orders.objects.filter(order_date__gte=week_ago).annotate(
        day=TruncDay('order_date')).values('day').annotate(total=Count('id'))
    order_days = [i.get('day').strftime("%a") for i in x]
    total_orders_day = [i.get('total') for i in x]
    q = Orders.objects.filter(order_date__gte=datetime.datetime.today()-datetime.timedelta(
        days=30), order_date__lte=datetime.datetime.today()).annotate(month=TruncMonth('order_date'), day=TruncDay('order_date')).values('month', 'day').annotate(total=Count('id')).order_by('month')
    context = {
        'subadmins': subadmins,
        'suppliers': suppliers,
        'products': products,
        'orders_day': orders_day,
        'orders_month': orders_month,
        'customers_day': customers_day,
        'customers_month': customers_month,
        'active_po': active_po,
        'completed_po': completed_po_count,
        'sum_completed_po': sum_completed_po,
        'transactions': len(transactions),
        'total_transaction_amount': total_transaction_amount,
        'present_month': present_month.strftime("%b"),
        'next_month': next_month.strftime("%b"),
        'order_days': order_days,
        'total_orders_day': total_orders_day,
        'q': q
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
