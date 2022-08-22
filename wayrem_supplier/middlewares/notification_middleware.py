from django.shortcuts import get_object_or_404
from wayrem_supplier.models import Notification, PurchaseOrder
from django.db.models import Q


class NotificationMiddleWare(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get('supplier_id'):
            notifications = Notification.objects.filter(supplier_id=request.session['supplier_id'],
                                                        status=False).order_by('created_at').reverse()
            active_po = PurchaseOrder.objects.filter(Q(supplier_name_id=request.session['supplier_id']) & ~Q(Q(status="declined") | Q(status="delivered"))).values(
                'po_name', 'supplier_name__company_name', 'po_id', 'status').distinct().count()
            request.active_po = active_po
            request.notifications = notifications
        response = self.get_response(request)
        return response
