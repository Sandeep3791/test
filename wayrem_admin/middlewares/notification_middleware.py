import imp
from django.shortcuts import get_object_or_404
from wayrem_admin.models import Notification
import datetime
from wayrem_admin.models_orders import Orders


class NotificationMiddleWare(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.po_notify or request.user.is_superuser:
                notifications = Notification.objects.filter(
                    status=True).order_by('created_at').reverse()[:10]
                request.notifications = notifications
                this_day = datetime.datetime.now().day
                request.order_today = Orders.objects.filter(
                    order_date__day=this_day).count()
                response = self.get_response(request)
        else:
            response = self.get_response(request)
        return response
