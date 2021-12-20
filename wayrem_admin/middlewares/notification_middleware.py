from django.shortcuts import get_object_or_404
from wayrem_admin.models import Notification


class NotificationMiddleWare(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        notifications = Notification.objects.filter(
            status=True).order_by('created_at').reverse()
        # Instead of using filter, consider doing (if it fits your usecase):
        # mycustom = get_object_or_404(MyCustom, pk=request.user.pk)
        request.notifications = notifications
        response = self.get_response(request)
        return response
