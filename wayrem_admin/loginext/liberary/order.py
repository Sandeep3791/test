from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.models_orders import OrderDetails
from datetime import datetime , timedelta  
import pytz
from wayrem_admin.models import Settings
from wayrem_admin.models import Warehouse

class Order(ApiBase):
    AUTHENTICATE_KEY=None
    DELIVERY_TIME='settings_delivery_time_slots'
    def get_total_items(self,order_id):
        total_items=OrderDetails.objects.filter(order_id=order_id).count()
        return total_items

    def get_authenticate_key(self):
        self.AUTHENTICATE_KEY=ApiBase.authenticate_secret_key(self)
        return self.AUTHENTICATE_KEY
    
    def create_order(self,order_details,account_code):
        create_order_dic=self.create_order_details(order_details,account_code)
        create_order_dic['shipmentCrateMappings']=self.shipping_box(order_details.id)
        create_order_list=[create_order_dic]
        method="POST"
        path="ShipmentApp/mile/v2/create"
        
        get_authenticate=self.get_authenticate_key()
        headers={'WWW-Authenticate':get_authenticate}
        response=ApiBase.send_request(self,method,path,create_order_list,headers,"json")
        return response

    def converttoutcdatetime(self,order_date):
        local = pytz.timezone("Asia/Riyadh")
        order_date=order_date.strftime("%Y-%m-%d %H:%M:%S")
        naive = datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        dtrer=utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return dtrer

    def addtimeorder(self,hours_end):
        order_end = datetime.now() + timedelta(hours=hours_end)
        return order_end

    def get_branch_name(self):
        get_branch_dic=Warehouse.objects.filter().first()
        branch_name=get_branch_dic.branch_name
        return branch_name

    def get_time(self):
        delivery_time =Settings.objects.values('value').filter(key=self.DELIVERY_TIME).first()
        if delivery_time is None:
            total_time=48
        else:
            total_time=delivery_time['value']
            total_time=int(total_time)
        return total_time

    def create_order_details(self,orderdetail,account_code):
        shipmentOrderDt=orderdetail.order_date # this in utc shipmentOrderDt
        shipmentOrderDt=self.converttoutcdatetime(shipmentOrderDt)
        #shipmentOrderDt=utc_dt
        branch_name=self.get_branch_name()
        distributionCenter=branch_name
        deliverBranch=branch_name

        priority='PRIORITY1'
        preparationTime=20
        paymentType='COD'
        packageValue=orderdetail.grand_total
        noofitems=self.get_total_items(orderdetail.id)
        start_time=datetime.now()
        deliver_start_window=self.converttoutcdatetime(start_time)
        deliverStartTimeWindow=deliver_start_window
        total_time=self.get_time()
        order_end_time=self.addtimeorder(total_time)
        deliver_end_window=self.converttoutcdatetime(order_end_time)
        deliverEndTimeWindow=deliver_end_window
        deliveryLocationType="Home"
        deliverAccountCode=account_code
        deliverAddressId="Home"
        deliverAccountName=orderdetail.order_ship_name
        deliverEmail=orderdetail.order_email
        deliverPhoneNumber=orderdetail.order_phone
        
        deliverApartment=orderdetail.order_ship_building_name
        deliverStreetName=orderdetail.order_ship_address
        deliverLandmark=orderdetail.order_ship_landmark
        deliverLocality=orderdetail.order_ship_region

        #deliverCity=orderdetail.order_city
        deliverCity=orderdetail.order_ship_region
        #deliverState="Riyadh"
        deliverCountry=orderdetail.order_country
        deliverPinCode="NA"
        deliverLatitude=orderdetail.order_ship_latitude
        deliverLongitude=orderdetail.order_ship_longitude
        returnBranch=branch_name

        deliveryLocationType=''
        create_order_dic={
                                "orderNo": orderdetail.ref_number,
                                "shipmentOrderTypeCd": "DELIVER",
                                "orderState": "FORWARD",
                                "shipmentOrderDt": shipmentOrderDt,
                                "distributionCenter":distributionCenter ,
                                "paymentType":paymentType,
                                "packageValue":packageValue,
                                "numberOfItems":noofitems,
                                "partialDeliveryAllowedFl": "Y",
                                "returnAllowedFl": "Y",
                                "cancellationAllowedFl": "N",    
                                "deliverBranch": deliverBranch,
                                "deliverEndTimeWindow": deliverEndTimeWindow,
                                "deliverStartTimeWindow": deliverStartTimeWindow,
                                "deliverAccountCode":deliverAccountCode,
                                #"deliverAddressId": deliverAddressId,
                                "deliverAccountName": deliverAccountName,
                                "deliverEmail":deliverEmail,
                                "deliverPhoneNumber":deliverPhoneNumber,
                                "deliverApartment": deliverApartment,
                                "deliverStreetName": deliverStreetName,
                                "deliverLandmark": deliverLandmark,
                                "deliverLocality": deliverLocality,
                                "deliverCity": deliverCity,
                                #"deliverState": deliverState,
                                "deliverCountry":deliverCountry,
                                "deliverPinCode": deliverPinCode,
                                "deliverLatitude":deliverLatitude,
                                "deliverLongitude":deliverLongitude, 
                                "returnBranch": returnBranch,
                            }
        return create_order_dic


    def shipping_box(self,order_id):
        orderdetails=OrderDetails.objects.filter(order_id=order_id)
        shippling_list=[]
        for orderdetail in orderdetails:
            shipping={}
            total_amount = ((float(orderdetail.price) + float(orderdetail.item_margin)) * float(orderdetail.quantity))-float(orderdetail.discount)
            shipping['crateCd']="CR0"+str(orderdetail.id)
            shipping['crateName']="Crate"+str(orderdetail.id)
            shipping['crateAmount']=total_amount
            shipping['crateType']="case"
            shipping['noOfUnits']=orderdetail.quantity
            #shipping['crateWeight']=10
            #shipping['crateVolume']=11
            #shipping['crateLength']=12
            #shipping['crateBreadth']=13
            #shipping['crateHeight']=14
            #shipping['crateTemperatureCategory']="Ambient"
            #shipping['crateMinTemperature']=10
            #shipping['crateMaxTemperature']=20
            shipping["shipmentlineitems"]=[{
                            "itemCd": orderdetail.product.SKU,
                            "itemName":orderdetail.product.name,
                            "itemPrice": float(orderdetail.price) + float(orderdetail.item_margin),
                            "itemQuantity": float(orderdetail.quantity),
                            #"itemType": "soup",
                            #"itemWeight": 10,
                            #"itemVolume":16,
                            #"itemLength":17,
                            #"itemBreadth":18,
                            #"itemHeight":19,
                            #"temperatureCategory":"Ambient",
                            #"minTemperature":10,
                            #"maxTemperature":15
            }]
            shippling_list.append(shipping)
        
        return shippling_list
                            


   