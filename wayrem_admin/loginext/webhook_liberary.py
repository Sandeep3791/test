import requests
import json,re
from wayrem_admin.models_orders import Orders,ShippingLoginextNotification,StatusMaster,OrderDeliveryLogs,OrderTransactions
from datetime import datetime
from wayrem_admin.forecasts.firebase_notify import FirebaseLibrary

class WebHookLiberary():
    def current_date_time(self,order_dic,order_reference_id):
        now = datetime.now()
        order_dic[order_reference_id]=now
        return order_dic

    def sendnotification(self,order_reference_id,status_id):
        order_id=self.get_order_id(order_reference_id)
        if order_id:
            FirebaseLibrary().send_notify(order_id=order_id,order_status=status_id)
        return 1
        
    def get_order_id(self,order_reference_id):
        get_order_id=Orders.objects.filter(order_tracking_number=order_reference_id).first()
        if get_order_id is None:
            return 0
        else:
            return get_order_id.id

    def get_order(self,order_dic):
        try:
            if 'reference_id' in order_dic:
                reference_id=order_dic['reference_id']
                p_id=ShippingLoginextNotification.objects.get(reference_id=reference_id)
                return p_id.id
            else:
                order_no=order_dic['order_no']
                order_ref_dic=Orders.objects.values('order_tracking_number').filter(ref_number=order_no).first()
                reference_id=order_ref_dic['order_tracking_number']
                p_id=ShippingLoginextNotification.objects.get(reference_id=reference_id)
                return p_id.id
        except:
            #reference_id=order_dic['reference_id']
            #print(ShippingLoginextNotification.objects.filter(reference_id=reference_id).query)
            return 0

    def get_order_payment_type(self,ship_log_not_id):
        if ship_log_not_id:
            p_id=ShippingLoginextNotification.objects.get(id=ship_log_not_id)
            return p_id.payment_mode
        else:
            return 0


    def saveorderrequest(self,create_order_dic,order_reference_id):
        shipping_loginext_notify=ShippingLoginextNotification.objects.filter(id=order_reference_id).update(**create_order_dic)
        
        return 1

    def dict_timestamp(self,order_dic,response_dic,responsekey):
        order_dic[responsekey]=response_dic['timestamp']
        return order_dic

    def create_dictonary(self,order_dic,response_dic,responsekey,valuetype="string"):
        
        if responsekey in response_dic:
            new_key=re.sub( '(?<!^)(?=[A-Z])', '_', responsekey).lower()
            if valuetype == "boolean":
                if str(response_dic[responsekey]) == 'false' or str(response_dic[responsekey]) == 'False': 
                    order_dic[new_key]=0
                else:
                    order_dic[new_key]=1
            elif valuetype == "date_time":
                order_dic[new_key]=(response_dic[responsekey])
            else:
                order_dic[new_key]=str(response_dic[responsekey])
            return order_dic
        else:
            return order_dic

    def createorderrequest(self,createorderrequest):
        order_dic={}
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'shipmentRequestNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'shipmentRequestDispatchDate')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'shipmentRequestType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'serviceType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickupAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickupAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliverAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliverAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'returnAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'returnAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'clientCode')
        order_dic=self.dict_timestamp(order_dic,createorderrequest,'orderrequest_timestamp')
        order_dic=self.current_date_time(order_dic,'created_at')
        order_dic=self.current_date_time(order_dic,'updated_at')
        return order_dic
    
    def createorder(self,createorderrequest):
        order_dic={}
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.dict_timestamp(order_dic,createorderrequest,'ordercreate_timestamp')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickupAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickupAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliverAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliverAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'returnAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'returnAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'clientCode')
        order_dic=self.current_date_time(order_dic,'updated_at')
        return order_dic

    def updateorder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'tripReferenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'numberOfItems')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'packageWeight')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'packageVolume')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'originAddr')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'destinationAddr')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'shipmentOrderTypeCd')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'clientNodeName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'clientNodeCd')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'address')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'shipmentNotes')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'assignmentMethod')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'vehicleNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'shipmentCrateMapping')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'startTimeWindow','date_time')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'endTimeWindow','date_time')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'calculatedStartDt','date_time')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'calculatedEndDt','date_time')
        return order_dic

    def orderstatusupdate(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'scanStatus')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'branchName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'scanTime')
        order_dic=self.current_date_time(order_dic,'updated_at')
        return order_dic

    def acceptedorder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        createorderrequest['orderState']=createorderrequest['status']
        createorderrequest['orderNo']=createorderrequest['clientShipmentId']
        createorderrequest['acceptedorderTimestamp']=createorderrequest['updatedOn']

        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumUserName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'carrierName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'carrierBranchName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'tripName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'acceptedorderTimestamp')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'trackUrl')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickupEndDate')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryEndDate')
        order_dic=self.current_date_time(order_dic,'updated_at')
        return order_dic

    def rejectedorder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        createorderrequest['orderNo']=createorderrequest['clientShipmentId']
        createorderrequest['orderState']=createorderrequest['status']
        createorderrequest['rejectedorderTimestamp']=createorderrequest['updatedOn']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'tripName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'rejectedorderTimestamp')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reasonOfRejection')
        return order_dic

    def cancelorder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'tripName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'cancellationTime')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reason')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reasonCd')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'cancelledBy')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'isCancelOccurAfterPickupFl','boolean')
        return order_dic

    def checkinorder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'tripName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumReferenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'locationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'checkInTime')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'checkinLatitude')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'checkinLongitude')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'parentOrderNo')
        return order_dic

    def deliveredorder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliverAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliverAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickupAccountCode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickupAddressId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'tripName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'branchName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerComment')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerRating')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryTime')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'cashAmount')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryLocationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'transactionId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'actualCashAmount')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'paymentMode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'recipientName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'paymentSubType')
        print(order_dic)
        return order_dic
    
    def attempteddeliveryorder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'branchName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'clientId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerComment')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerRating')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reasonCd')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reason')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryTime','date_time')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryLocationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'recipientName')
        return order_dic

    def pickeduporder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        createorderrequest['orderStatus']=createorderrequest['status']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'branchName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerComment')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerRating')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderStatus')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'latitude')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'longitude')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'pickedUpTime')
        return order_dic
    
    def orderattemptedpickuporder(self,createorderrequest):
        order_dic={}
        createorderrequest['referenceId']=createorderrequest['orderReferenceId']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'referenceId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerComment')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerRating')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reasonCd')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reason')
        return order_dic
    
    def partiallydeliveredorder(self,createorderrequest):
        order_dic={}
        createorderrequest['shipmentCrateMapping']=createorderrequest['shipmentCrateMappingList']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderNo')
        createorderrequest['orderStatus']=createorderrequest['statusCd']
        order_dic=self.create_dictonary(order_dic,createorderrequest,'notificationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderLeg')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'awbNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerComment')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerRating')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryMediumName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'phoneNumber')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderState')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'customerName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reasonCd')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'reason')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'orderStatus')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryTime','date_time')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'cashAmount')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'deliveryLocationType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'branchName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'transactionId')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'paymentMode')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'recipientName')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'actualCashAmount')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'paymentSubType')
        order_dic=self.create_dictonary(order_dic,createorderrequest,'shipmentCrateMapping')
        return order_dic


    def get_order_id(self,order_dic):
        try:
            if 'reference_id' in order_dic:
                reference_id=order_dic['reference_id']
                p_id=Orders.objects.filter(order_tracking_number=reference_id).first()
                return p_id
            else:
                order_no=order_dic['order_no']
                order_ref_dic=Orders.objects.filter(ref_number=order_no).first()
                p_id=Orders.objects.filter(order_tracking_number=reference_id).first()
                return p_id
        except:
            return 0
    def status_update_order(self,reference_dic,delivery_status):
        order_reference_det=self.get_order_id(reference_dic)
        if order_reference_det is not None:
            order_id=order_reference_det.id
            deliv_obj_stat_instance=StatusMaster.objects.get(id=delivery_status)
            order_update=Orders.objects.filter(id=order_id).update(delivery_status=deliv_obj_stat_instance)
            now = datetime.now()
            odl=OrderDeliveryLogs(order_id=order_id,order_status=deliv_obj_stat_instance,order_status_details="status change",log_date=now,user_id=1,customer_view=deliv_obj_stat_instance.customer_view)
            odl.save()

    def update_payment_status(self,reference_dic):
        order_reference_det=self.get_order_id(reference_dic)
        if order_reference_det is not None:
            order_id=order_reference_det.id
            transaction_instance=StatusMaster.objects.get(id=7)
            OrderTransactions.objects.filter(order_id=order_id).update(payment_status=transaction_instance)
            return 1