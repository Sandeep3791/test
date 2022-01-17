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


class LogiNextAPI(ApiBase,viewsets.ViewSet):
    def test(self,request,survey_id=None):
        status=HTTP_200_OK
        result={'message':"all ready exist"}
        result_build=Response(result,status=status)
        return result_build
    
    def authenticate(self,request):
          
        get_secret_key=ApiBase.authenticate_secret_key(self)
        print(get_secret_key)
        return HttpResponse("kapil")
    
    