from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.loginext.liberary.order import Order
from wayrem_admin.models_orders import Orders


class LoginextOrderCreate(Order):
    #customerlib=Customer()
    
    def get_order(self,order_id):
        try:
            order_det=Orders.objects.filter(id=order_id).first()
        except Orders.DoesNotExist:
            order_det = None
        finally:
            return order_det

    def ordercreate(self,order_id):
        '''
            Customer Create 
            Customer Address create/update
            Orderrequest create
            orderrequest
        '''
        order_details=self.get_order(order_id)
        response=self.create_order(order_details)
        order_tracking_number=self.get_reference(response)
        if order_tracking_number:
            order_tracking_number=self.update_order(order_id,order_tracking_number)
        return order_id

    def get_reference(self,response):
        reference_id=None
        if int(response['status']) == 200:
            data=response['data']
            for data_reference in data:
                reference_id=data_reference['referenceId']
        return reference_id

    def update_order(self,order_id,order_tracking_number):
        order_update=Orders.objects.filter(id=order_id).update(order_tracking_number=order_tracking_number)
        return 1
