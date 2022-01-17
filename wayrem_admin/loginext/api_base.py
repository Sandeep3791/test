from abc import ABC, abstractmethod
import requests
import json

class ApiBase(ABC):

    def get_credentials(self):
        credentials={}
        credentials['userName']="raghad.baeshen@rahal.mynaghi.com"
        credentials['password']="Rb123456"
        credentials['base_path']="https://api.loginextsolutions.com/"
        return credentials

    def send_request(self, method, path, params,headers={},data_type="json"):   
        cred=ApiBase.get_credentials(self)
        base_path = cred['base_path']          
        if(method == 'get' or method == 'GET'):
            if headers:            
                resp = requests.get(base_path+path,headers=headers)
            else:
                resp = requests.get(base_path+path)
        if(method == 'post' or method == 'POST'):
            if headers:
                if data_type == "data":
                    resp = requests.post(base_path+path, data=params, headers=headers)
                elif data_type == "json":
                    resp = requests.post(base_path+path, json=params, headers=headers)                
            else:
                if data_type == "data":
                    resp = requests.post(base_path+path, data=params)
                elif data_type == "json":
                    resp = requests.post(base_path+path, json=params)
                    
        if(method == 'put' or method == 'PUT'):
            if headers:
                if data_type == "data":
                    resp = requests.put(base_path+path, data=params, headers=headers)
                elif data_type == "json":
                    resp = requests.put(base_path+path, json=params, headers=headers)                
            else:
                if data_type == "data":
                    resp = requests.put(base_path+path, data=params)
                elif data_type == "json":
                    resp = requests.put(base_path+path, json=params)                                       
        return resp.json()

    def authenticate_secret_key(self,method="POST",path="LoginApp/login/authenticate",headers={},data_type="json"):   
        cred=ApiBase.get_credentials(self)
        base_path = cred['base_path']          
        params={"userName":cred['userName'],"password":cred['password']}
        if(method == 'post' or method == 'POST'):
            if headers:
                if data_type == "data":
                    resp = requests.post(base_path+path, data=params, headers=headers)
                elif data_type == "json":
                    resp = requests.post(base_path+path, json=params, headers=headers)                
            else:
                if data_type == "data":
                    resp = requests.post(base_path+path, data=params)
                elif data_type == "json":
                    resp = requests.post(base_path+path, json=params)
        get_data=resp.json()
        get_header_details=resp.headers
        if get_data['status'] == 200:
            secret_key=get_header_details['WWW-Authenticate']
        else:
            secret_key=None
        return secret_key