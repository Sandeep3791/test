import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import HttpResponse
import json
from wayrem_admin.loginext.webhook_liberary import WebHookLiberary
from wayrem_admin.utils.constants import *

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextCreateRequestAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.createorderrequest(create)    
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextCreateOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.createorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextUpdateOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.updateorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextorderStatusUpdateAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.orderstatusupdate(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextAcceptedOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.acceptedorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextRejectedOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.rejectedorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextCancelOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.cancelorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_CANCELLED)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextCheckinOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.checkinorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextDeliveredOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.deliveredorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_DELIVERED)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextAttemptedDeliveryOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.attempteddeliveryorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_ATTEMPTED_DELIVERED)
        self.webhook.status_update_order(create_order_dic,ORDER_RETURNED_WAREHOUSE)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextPartiallyDeliveredOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.partiallydeliveredorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_PARTIALLY_DELIVERED)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextPickedupOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.pickeduporder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_PICKUP)
        return HttpResponse({'message':'Success'})

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextOrderAttemptedPickupOrderAPI(View):
    webhook=WebHookLiberary()
    @csrf_exempt
    def post(self, request, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        create=body
        create_order_dic=self.webhook.orderattemptedpickuporder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_ATTEMPTED_PICKUP)
        return HttpResponse({'message':'Success'})