from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.loginext.liberary.order import Order
from wayrem_admin.loginext.liberary.customer import CustomerLib
from wayrem_admin.models import Orders, ShippingLoginextNotification


class LoginextOrderCreate(Order, CustomerLib):
    # customerlib=Customer()

    def get_order(self, order_id):
        try:
            order_det = Orders.objects.filter(id=order_id).first()
        except Orders.DoesNotExist:
            order_det = None
        finally:
            return order_det

    def ordercreate(self, order_id):
        '''
            Customer Create 
            Customer Address create/update
            Orderrequest create
            orderrequest
        '''

        order_details = self.get_order(order_id)
        if order_details.order_tracking_number is None or order_details.order_tracking_number == "":
            # create customer detail in loginext
            account_code = self.process_customer(order_details)
            # hit the loginext api for shipping
            response = self.create_order(order_details, account_code)
            self.storing_response(order_id, response)
            order_tracking_number = self.get_reference(response)
            if order_tracking_number:
                self.update_order(order_id, order_tracking_number)
                self.insert_shipping_loginext_notification(
                    order_tracking_number)
                return 1
            else:
                return 0
        else:
            return 2

    def storing_response(self, order_id, response):
        order_update = Orders.objects.filter(
            id=order_id).update(order_shipping_response=response)
        return 1

    def insert_shipping_loginext_notification(self, reference_id):
        s_notifaction = ShippingLoginextNotification.objects.filter(
            reference_id=reference_id).count()
        if s_notifaction == 0:
            shippingnotification = ShippingLoginextNotification(
                reference_id=reference_id)
            shippingnotification.save()
        else:
            print("already created")
        return 1

    def get_reference(self, response):
        reference_id = None
        if int(response['status']) == 200:
            data = response['data']
            for data_reference in data:
                reference_id = data_reference['referenceId']
        return reference_id

    def update_order(self, order_id, order_tracking_number):
        order_update = Orders.objects.filter(id=order_id).update(
            order_tracking_number=order_tracking_number)
        return 1
