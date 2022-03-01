from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
# Create your views here.
from django.core import serializers
import collections,json,base64

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
import uuid,hashlib,requests,json,base64
from django.conf import settings
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,HTTP_403_FORBIDDEN
)
from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.loginext.webhook_liberary import WebHookLiberary
from wayrem_admin.utils.constants import *
from rest_framework.permissions import AllowAny
import sys, traceback, gc
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class LogiNextWeebHookOrderAPI(ApiBase,WebHookLiberary,viewsets.ViewSet):
    webhook=WebHookLiberary()
    permission_classes = (AllowAny,)
    
    permission_classes_by_action = {'createorder': [AllowAny],}
    @csrf_exempt
    def createorderrequest(self,request):
        create=request.data
        create_order_dic=self.webhook.createorderrequest(create)    
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"updated"}
        result_build=Response(result,status=status)
        return result_build

      
    @csrf_exempt
    def createorder(self,request):
        try:
            create=request.data
            create_order_dic=self.webhook.createorder(create)
            order_reference_id=self.webhook.get_order(create_order_dic)
            
            self.webhook.saveorderrequest(create_order_dic,order_reference_id)
            status=HTTP_200_OK
            result={'message':"create order"}
            result_build=Response(result,status=status)
            return result_build
        except:
            the_page = sys.exc_info()
            trck= traceback.format_exc()
            print(the_page)
            print(trck)
            raise

    @csrf_exempt
    def updateorder(self,request):
        create=request.data
        create_order_dic=self.webhook.updateorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        # pending
        result={'message':"update order"}
        result_build=Response(result,status=status)
        return result_build

    @csrf_exempt
    def orderstatusupdate(self,request):
        create=request.data
        create_order_dic=self.webhook.orderstatusupdate(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"orderstatusupdate"}
        result_build=Response(result,status=status)
        return result_build

    @csrf_exempt
    def acceptedorder(self,request):
        create=request.data
        create_order_dic=self.webhook.acceptedorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"acceptedorder"}
        result_build=Response(result,status=status)
        return result_build
    
    def rejectedorder(self,request):
        create=request.data
        create_order_dic=self.webhook.rejectedorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"rejectedorder"}
        result_build=Response(result,status=status)
        return result_build

    def cancelorder(self,request):
        create=request.data
        create_order_dic=self.webhook.cancelorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_CANCELLED)
        status=HTTP_200_OK
        result={'message':"Cancel order"}
        result_build=Response(result,status=status)
        return result_build

    def checkinorder(self,request):
        create=request.data
        create_order_dic=self.webhook.checkinorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"Checkin order"}
        result_build=Response(result,status=status)
        return result_build
    
    def deliveredorder(self,request):
        create=request.data
        create_order_dic=self.webhook.deliveredorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_DELIVERED)
        status=HTTP_200_OK
        result={'message':"delivered order"}
        result_build=Response(result,status=status)
        return result_build
    
    def attempteddeliveryorder(self,request):
        create=request.data
        create_order_dic=self.webhook.attempteddeliveryorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_ATTEMPTED_DELIVERED)
        self.webhook.status_update_order(create_order_dic,ORDER_RETURNED_WAREHOUSE) 
        status=HTTP_200_OK
        result={'message':"attempted delivery order"}
        result_build=Response(result,status=status)
        return result_build

    def partiallydeliveredorder(self,request):
        create=request.data
        create_order_dic=self.webhook.partiallydeliveredorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_PARTIALLY_DELIVERED)
        status=HTTP_200_OK
        result={'message':"partially delivered order"}
        result_build=Response(result,status=status)
        return result_build

    def pickeduporder(self,request):
        create=request.data
        create_order_dic=self.webhook.pickeduporder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_PICKUP)
        status=HTTP_200_OK
        result={'message':"picked up order"}
        result_build=Response(result,status=status)
        return result_build
    
    def orderattemptedpickuporder(self,request):
        create=request.data
        create_order_dic=self.webhook.orderattemptedpickuporder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        self.webhook.status_update_order(create_order_dic,ORDER_DELIVERY_ATTEMPTED_PICKUP)
        status=HTTP_200_OK
        result={'message':"order attempted pickup order"}
        result_build=Response(result,status=status)
        return result_build