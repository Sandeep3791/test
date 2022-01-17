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
from wayrem_admin.loginext.api_base import ApiBase
from wayrem_admin.loginext.webhook_liberary import WebHookLiberary

class LogiNextWeebHookOrderAPI(ApiBase,WebHookLiberary,viewsets.ViewSet):
    webhook=WebHookLiberary()

    def createorderrequest(self,request):
        create=request.data
        create_order_dic=self.webhook.createorderrequest(create)    
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"updated"}
        result_build=Response(result,status=status)
        return result_build

    def createorder(self,request):
        create=request.data
        create_order_dic=self.webhook.createorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"create order"}
        result_build=Response(result,status=status)
        return result_build
    
    def updateorder(self,request):
        create=request.data
        create_order_dic=self.webhook.updateorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        print(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)

        status=HTTP_200_OK
        # pending
        result={'message':"update order"}
        result_build=Response(result,status=status)
        return result_build

    def orderstatusupdate(self,request):
        create=request.data
        create_order_dic=self.webhook.orderstatusupdate(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"orderstatusupdate"}
        result_build=Response(result,status=status)
        return result_build

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
        status=HTTP_200_OK
        result={'message':"delivered order"}
        result_build=Response(result,status=status)
        return result_build
    
    def attempteddeliveryorder(self,request):
        create=request.data
        create_order_dic=self.webhook.attempteddeliveryorder(create)
        order_reference_id=self.webhook.get_order(create_order_dic)
        self.webhook.saveorderrequest(create_order_dic,order_reference_id)
        status=HTTP_200_OK
        result={'message':"attempted delivery order"}
        result_build=Response(result,status=status)
        return result_build


