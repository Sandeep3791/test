from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.models import OrderDetails, OrderLoginextShipment
from datetime import datetime, timedelta
import pytz
from wayrem_admin.models import Settings
from wayrem_admin.models import Warehouse


class CustomerLib(ApiBase):
    LOGINEXT_CUSTOMER_PREFIX = 'loginext_customer_prefix'
    LOGINEXT_CUSTOMER_TYPE = 'loginext_customer_type'

    def __init__(self):
        loginext_customer_prefix = Settings.objects.filter(
            key=self.LOGINEXT_CUSTOMER_PREFIX).first()
        loginext_customer_type = Settings.objects.filter(
            key=self.LOGINEXT_CUSTOMER_TYPE).first()
        self.customer_type = loginext_customer_type.value.lower()
        self.customer_prefix = loginext_customer_prefix.value.lower()

    def get_authenticate_key(self):
        self.AUTHENTICATE_KEY = ApiBase.authenticate_secret_key(self)
        return self.AUTHENTICATE_KEY

    def accountcode(self, customer_id):
        get_accountcode = self.customer_prefix+"_"+str(customer_id)
        return get_accountcode

    def get_customer_id(self, customer_id):
        get_customer = OrderLoginextShipment.objects.filter(
            customer=customer_id).first()
        if get_customer is None:
            return 0
        else:
            return get_customer

    def check_customer(self):
        method = "GET"
        path = "ClientApp/customer/v1/get/list?ids=wayrem1"
        get_authenticate = self.get_authenticate_key()
        headers = {'WWW-Authenticate': get_authenticate}
        response = ApiBase.send_request(self, method, path, [], headers)
        if response['status'] == 200:
            return response['data'][0]
        else:
            return 0

    def process_customer(self, order_details):
        account_code = self.accountcode(order_details.customer.id)
        is_account_exist = self.get_customer_id(order_details.customer.id)
        get_customer_data = self.check_customer()
        if is_account_exist:
            if is_account_exist.customer_reference_id is None:
                if get_customer_data:
                    insert_customer_response = {'id': is_account_exist.id, 'customer_id': order_details.customer.id, 'customer_account_code': account_code,
                                                'customer_reference_id': get_customer_data["referenceId"], 'create_customer_response': get_customer_data}
                    self.insert_customer_response(insert_customer_response)
                    reference_id = get_customer_data["referenceId"]
                    update_customer = self.update_customer(
                        order_details, reference_id)
                else:
                    create_customer_response = self.create_customer(
                        order_details, account_code)
                    customer_reference_id = self.get_customer_reference(
                        create_customer_response)
                    insert_customer_response = {'id': is_account_exist.id, 'customer_id': order_details.customer.id, 'customer_account_code': account_code,
                                                'customer_reference_id': customer_reference_id, 'create_customer_response': create_customer_response}
                    self.insert_customer_response(insert_customer_response)
            else:
                reference_id = is_account_exist.customer_reference_id
                update_customer = self.update_customer(
                    order_details, reference_id)
                insert_customer_response = {'id': is_account_exist.id, 'customer_id': order_details.customer.id,
                                            'customer_account_code': account_code, 'customer_reference_id': reference_id, 'create_customer_response': update_customer}
                self.insert_customer_response(insert_customer_response)
        else:
            if get_customer_data:
                insert_customer_response = {'customer_id': order_details.customer.id, 'customer_account_code': account_code,
                                            'customer_reference_id': get_customer_data["referenceId"], 'create_customer_response': get_customer_data}
                self.insert_customer_response(insert_customer_response)
                reference_id = get_customer_data["referenceId"]
                update_customer = self.update_customer(
                    order_details, reference_id)
            else:
                create_customer_response = self.create_customer(
                    order_details, account_code)
                customer_reference_id = self.get_customer_reference(
                    create_customer_response)
                if customer_reference_id:
                    insert_customer_response = {'customer_id': order_details.customer.id, 'customer_account_code': account_code,
                                                'customer_reference_id': customer_reference_id, 'create_customer_response': create_customer_response}
                    self.insert_customer_response(insert_customer_response)
                else:
                    insert_customer_response = {'customer_id': order_details.customer.id, 'customer_account_code': account_code,
                                                'customer_reference_id': None, 'create_customer_response': create_customer_response}
                    self.insert_customer_response(insert_customer_response)
        return account_code

    def get_customer_reference(self, response):
        reference_id = None
        if int(response['status']) == 200:
            data = response['data']
            for data_reference in data:
                reference_id = data_reference['referenceId']
        return reference_id

    def insert_customer_response(self, insert_customer_response):
        order_customer_response = OrderLoginextShipment(
            **insert_customer_response)
        order_customer_response.save()

    def create_customer(self, order_details, account_code):
        create_customer = self.create_customer_dic(order_details, account_code)
        method = "POST"
        path = "ClientApp/customer/v1/create"
        get_authenticate = self.get_authenticate_key()
        headers = {'WWW-Authenticate': get_authenticate}
        response = ApiBase.send_request(
            self, method, path, create_customer, headers, "json")
        return response

    def create_customer_dic(self, order_details, account_code):
        create_customer_dic = {}
        create_customer_dic['accountCode'] = account_code
        if order_details.customer.last_name is None:
            last_name = ""
        else:
            last_name = order_details.customer.last_name

        create_customer_dic['name'] = order_details.customer.first_name+last_name
        create_customer_dic['mobile'] = order_details.customer.contact
        create_customer_dic['email'] = order_details.customer.email
        create_customer_dic['customerType'] = self.customer_type
        create_customer_dic['billingAddress'] = {}
        create_customer_dic['billingAddress']['apartment'] = order_details.order_ship_building_name
        create_customer_dic['billingAddress']['streetName'] = order_details.order_ship_address
        create_customer_dic['billingAddress']['landmark'] = order_details.order_ship_landmark

        create_customer_dic['billingAddress']['locality'] = order_details.order_ship_region
        create_customer_dic['billingAddress']['city'] = order_details.order_city
        create_customer_dic['billingAddress']['state'] = order_details.order_ship_region

        create_customer_dic['billingAddress']['country'] = order_details.order_country
        create_customer_dic['billingAddress']['pincode'] = "NA"
        create_customer_dic['billingAddress']['latitude'] = order_details.order_ship_latitude
        create_customer_dic['billingAddress']['longitude'] = order_details.order_ship_longitude
        create_customer = [create_customer_dic]
        return create_customer

    def update_customer(self, order_details, reference_id):
        update_customer = self.update_customer_dic(order_details, reference_id)
        method = "POST"
        path = "ClientApp/customer/v1/update"
        get_authenticate = self.get_authenticate_key()
        headers = {'WWW-Authenticate': get_authenticate}
        response = ApiBase.send_request(
            self, method, path, update_customer, headers, "json")
        return response

    def update_customer_dic(self, order_details, reference_id):
        update_customer_dic = {}
        if order_details.customer.last_name is None:
            last_name = ""
        else:
            last_name = order_details.customer.last_name
        update_customer_dic['referenceId'] = reference_id
        update_customer_dic['name'] = order_details.customer.first_name+last_name
        update_customer_dic['mobile'] = order_details.customer.contact
        update_customer_dic['email'] = order_details.customer.email
        update_customer_dic['customerType'] = self.customer_type
        update_customer_dic['billingAddress'] = {}
        update_customer_dic['billingAddress']['apartment'] = order_details.order_ship_building_name
        update_customer_dic['billingAddress']['streetName'] = order_details.order_ship_address
        update_customer_dic['billingAddress']['landmark'] = order_details.order_ship_landmark
        update_customer_dic['billingAddress']['locality'] = order_details.order_ship_region
        update_customer_dic['billingAddress']['city'] = order_details.order_city
        update_customer_dic['billingAddress']['state'] = order_details.order_city
        update_customer_dic['billingAddress']['country'] = order_details.order_country
        update_customer_dic['billingAddress']['pincode'] = "NA"
        update_customer_dic['billingAddress']['latitude'] = order_details.order_ship_latitude
        update_customer_dic['billingAddress']['longitude'] = order_details.order_ship_longitude
        update_customer = [update_customer_dic]
        return update_customer
