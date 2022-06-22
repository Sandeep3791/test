from wayrem_admin.forms import warehouse
from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.models import Orders, ShippingLoginextNotification, OrderDetails, OrderTransactions, StatusMaster, ShippingRates, create_new_ref_number
from wayrem_admin.models import RecurrentType, RecurrenceGrocery, GroceryMaster, GroceryProducts
from wayrem_admin.models import Settings, CustomerAddresses, Warehouse, Inventory
from wayrem_admin.utils.constants import *
from datetime import timedelta, date, datetime
from django.db.models import Sum, F
import googlemaps
from wayrem_admin.forecasts.firebase_notify import FirebaseLibrary
import math

class OrderLiberary:
    tax_vat = SETTING_VAT
    invoice_default = INVOICE_DEFAULT
    free_shipping_total = FREE_SHIPPING_TOTAL
    paid_shipping_charge = PAID_SHIPPING_CHARGE
    DELIVERY_FREE_CHARGE_AFTER_AMOUNT="delivery_free_charge_after_amount"
    GOOGLE_MAP_KEY="AIzaSyCT93vNszQ2b8JQmHqrkDTVJnjVKmHSaTc"
    DELIVERY_FREE_CHARGE_BELOW_RANGE="delivery_free_charge_below_range"
    DELIVERY_CHARGE_BASE_FEE="delivery_charge_base_fee"
    DELIVERY_FEE_DISTANCE_CHARGE="delivery_fee_distance_charge"
    SHIPPING_RATES_AFTER_BASEFARE="shipping_rates_after_basefare"

    def __init__(self):
        self.recurrence_type = self.recurrent_type()
        self.today_date = date.today()
        self.delivery_order_per_day = self.get_setting_value(DELIVERY_ORDER_PER_DAY)
        #self.customer_approve_per_day = self.get_setting_value(CUSTOMER_APPROVAL_PER_DAY)

    def recurrent_type(self):
        recurrence_type = RecurrentType.objects.filter(
            status=1).order_by('value')
        return recurrence_type

    def proccess_order(self):
        get_date = self.get_filter_data()
        recurrence_grocery = self.recurrence_grocery(get_date)
        if recurrence_grocery:
            self.create_recurrence_grocery_order(recurrence_grocery)

    def get_setting_value(self, keys):
        get_setting = Settings.objects.filter(key=keys).first()
        return int(get_setting.value)

    def get_filter_data(self):
        #total_day = self.today_date + timedelta(days=self.delivery_order_per_day) + timedelta(days=self.customer_approve_per_day)
        total_day = self.today_date + timedelta(days=self.delivery_order_per_day) 
        return total_day

    def recurrence_grocery(self, get_date):
        recurrence_groccery = RecurrenceGrocery.objects.filter(
            status=1, recurrence_nextdate=get_date)
        
        return recurrence_groccery

    def create_recurrence_grocery_order(self, recurrence_grocery):
        for rg in recurrence_grocery:
            is_order_created = self.create_order_recurrence(rg)
            if is_order_created:
                self.update_recurrence_groccery(rg)  # update nextdate
        return 1

    def update_recurrence_groccery(self, rg):
        no_of_days = rg.recurrenttype.value
        no_of_days = int(no_of_days)
        current_date_next = datetime.strptime(
            rg.recurrence_nextdate, "%Y-%m-%d").date()
        re_date = current_date_next + timedelta(days=no_of_days)
        RecurrenceGrocery.objects.filter(id=rg.id).update(
            recurrence_nextdate=re_date, updated_at=datetime.now())
        self.update_grocery_products(rg.grocery_id, re_date)
        return 1

    def update_grocery_products(self, grocery_id, next_date):
        groc_product = GroceryProducts.objects.filter(grocery_id=grocery_id)
        for groc_products in groc_product:
            groc_products.recurrence_nextdate = next_date
            groc_products.save()
        return 1

    def create_order_recurrence(self, order_recurrence):
        cur_grocery_id = order_recurrence.grocery_id
        grocery_product_list = self.get_grocery_product(order_recurrence)
        order_id = self.create_order(order_recurrence, grocery_product_list)

        if order_id:
            self.create_order_detail(
                order_id, order_recurrence, grocery_product_list)
            self.create_order_transactions(order_id, order_recurrence)
            Inventory().order_inventory_process(order_id)
            FirebaseLibrary().send_notify(order_id=order_id,
                                          order_status=23, grocery_id=cur_grocery_id)

        return order_id

    def check_is_order_created(self, grocery_product_list):
        is_order_created_qty = 0
        for gpl in grocery_product_list:
            quantity = float(gpl.product_qty)
            product_quantity = float(gpl.product.quantity)
            product_threshold = float(gpl.product.outofstock_threshold)
            total_quantity_demand = quantity+product_threshold
            if product_quantity >= total_quantity_demand:
                is_order_created_qty = 1
        return is_order_created_qty
        # quantity,outofstock_threshold

    def total_product_qty_exist(self, product_det, quantity):
        quantity = float(quantity)
        product_quantity = float(product_det.quantity)
        product_threshold = float(product_det.outofstock_threshold)
        total_quantity_demand = quantity+product_threshold
        if product_quantity >= total_quantity_demand:
            return quantity
        return float(0)

    def create_order(self, order_recurrence, grocery_product_list):
        try:
            is_order_created_qty = self.check_is_order_created(
                grocery_product_list)
            if not is_order_created_qty:
                # order not created add new next date
                self.update_recurrence_groccery(order_recurrence)
                return 0

            customer_id = order_recurrence.customer.id
            customer_address = self.get_customer_address(
                order_recurrence.grocery.address.id)
            ref_number = self.get_ref_number()
            tax_vat = self.get_tax_vat()
            product_total = self.product_total(grocery_product_list)

            sub_total = round(product_total['sub_total'], 2)
            item_margin = round(product_total['item_margin'], 2)
            total = round(product_total['total'], 2)

            if customer_address is None:
                order_lat = order_recurrence.customer.billlingAddress_Latitude
                order_long = order_recurrence.customer.billingAddress_longitude
            else:
                order_lat = customer_address.deliveryaddress_latitude
                order_long = customer_address.deliveryaddress_longitude

            #shipping = self.get_shipping_value(order_lat,order_long)
            shipping = self.get_shipping_value(total,order_lat,order_long)
            

            promo = 0
            item_discount = round(product_total['item_discount'], 2)
            discount = round(product_total['discount'], 2)
            grand_total, tax = self.get_grand_total(total, tax_vat, shipping)
            full_name = customer_address.full_name

            order_ship_name = full_name
            #order_ship_address = order_recurrence.customer.billing_country+", " + customer_address.region+", " + customer_address.landmark+", " + order_recurrence.customer.delivery_house_no_building_name
            order_ship_address = "Saudi Arabia, " + customer_address.region + ", " + customer_address.town_city + \
                ", " + customer_address.landmark+", " + customer_address.house_no_building_name

            order_ship_building_name = customer_address.house_no_building_name

            order_ship_landmark = customer_address.landmark
            order_ship_region = customer_address.region
            order_ship_latitude = order_lat
            order_ship_longitude = order_long
            order_billing_name = full_name
            order_billing_address = "Saudi Arabia, " + order_recurrence.customer.billing_region + ", " + order_recurrence.customer.billing_town_city + \
                ", " + order_recurrence.customer.billing_landmark+", " + \
                order_recurrence.customer.billing_house_no_building_name

            order_city = order_recurrence.customer.delivery_town_city
            order_country = "SAU"
            order_phone = order_recurrence.customer.contact
            order_email = order_recurrence.customer.email
            currentTimeDate = datetime.now() + timedelta(days=1)
            order_date = currentTimeDate
            order_shipped = 0

            order_tracking_number = None
            content = None
            customer_id = customer_id
            delivery_status = StatusMaster(id=1)
            # status = StatusMaster(id=23) on phase 2 this will recurrent pending for approval.
            status = StatusMaster(id=16)
            order_shipping_response = None
            order_type = StatusMaster(id=25)

            order_dic = {'ref_number': ref_number, 'sub_total': sub_total, 'item_discount': item_discount, 'item_margin': item_margin, 'tax': tax, 'tax_vat': tax_vat, 'shipping': shipping, 'total': total, 'promo': promo, 'discount': discount, 'grand_total': grand_total, 'order_ship_name': order_ship_name, 'order_ship_address': order_ship_address, 'order_ship_building_name': order_ship_building_name, 'order_ship_landmark': order_ship_landmark, 'order_ship_region': order_ship_region, 'order_ship_latitude': order_ship_latitude, 'order_ship_longitude': order_ship_longitude, 'order_billing_name': order_billing_name,
                         'order_billing_address': order_billing_address, 'order_city': order_city, 'order_country': order_country, 'order_phone': order_phone, 'order_email': order_email, 'order_date': order_date, 'order_shipped': order_shipped, 'order_tracking_number': order_tracking_number, 'content': content, 'customer_id': customer_id, 'delivery_status': delivery_status, 'status': status,
                         'order_shipping_response': order_shipping_response, 'order_type': order_type}

            order_cr = Orders(**order_dic)
            order_cr.save()
            return order_cr.id

        except Exception as e:
            print(e)
            return 0

    def get_shipping_value_new(self, total_amount):
        if total_amount > float(self.free_shipping_total):
            return 0
        else:
            paid_shipping_charge = self.get_setting_value(
                self.paid_shipping_charge)
            return paid_shipping_charge

    def get_shipping_value(self, total_amount,customer_latitude, customer_longitude):
        delivery_free_charge_below_range = Settings.objects.get(key=self.DELIVERY_FREE_CHARGE_AFTER_AMOUNT)
        free_shipping_total=delivery_free_charge_below_range.value
        if total_amount > float(free_shipping_total):
            return float(0)
        gmaps = googlemaps.Client(key=self.GOOGLE_MAP_KEY)
        warehouse = Warehouse.objects.filter(status="Active").first()
        warehouse_latitude = warehouse.latitude
        warehouse_longitude = warehouse.longitude
        origin_latitude = float(warehouse_latitude)
        origin_longitude = float(warehouse_longitude)
        destination_latitude = float(customer_latitude)
        destination_longitude = float(customer_longitude)
        #destination_latitude ="24.692387"
        #destination_longitude ="46.725090"
        distance = gmaps.distance_matrix([str(origin_latitude) + " " + str(origin_longitude)], [str(
                destination_latitude) + " " + str(destination_longitude)], mode='driving')['rows'][0]['elements'][0]
        
        x = distance.get("distance").get('value')
        y = float(x/1000)
        calculate_price = self.calculate_price_km(y)
        return calculate_price

    def calculate_price_km(self, km):
        km = float(km)
        delivery_free_charge_below_range = Settings.objects.get(key=self.DELIVERY_FREE_CHARGE_BELOW_RANGE)
        free_delivery_before_range=delivery_free_charge_below_range.value
        if km <= float(free_delivery_before_range):
            return float(0)
        else:
            delivery_charge = Settings.objects.get(key=self.DELIVERY_CHARGE_BASE_FEE)
            basic_charge=float(delivery_charge.value)-float(3)
            delivery_fee_distance_charge=Settings.objects.get(key=self.DELIVERY_FEE_DISTANCE_CHARGE)
            include_fees_after_km=delivery_fee_distance_charge.value
            shipping_rates_after_basefare=Settings.objects.get(key=self.SHIPPING_RATES_AFTER_BASEFARE)
            shipping_rates=shipping_rates_after_basefare.value
            total_value=km/float(include_fees_after_km)
            caluclate_dis=math.floor(total_value)
            total_price=(float(caluclate_dis)*float(shipping_rates))+basic_charge
            return total_price

    def product_total(self, grocery_product_list):
        subtotal_unit_price = 0
        product_total = {}
        total_item_discount = 0
        total_item_margin = 0
        for gpl in grocery_product_list:
            quantity = float(gpl.product_qty)
            quantity = self.total_product_qty_exist(gpl.product, quantity)
            if quantity:
                product_subtotal = float(gpl.product.price)
                product_margin_amount = self.calculate_price_unit_type(
                    gpl.product.wayrem_margin, gpl.product.price, gpl.product.margin_unit)
                if gpl.product.discount is None:
                    product_discount_price = 0
                    total_price_margin = product_subtotal+product_margin_amount
                else:
                    product_discount_price = gpl.product.discount
                    total_price_margin = product_subtotal+product_margin_amount
                total_product_discount_price = self.calculate_price_unit_type(
                    product_discount_price, total_price_margin, gpl.product.dis_abs_percent)

                subtotal_unit_price += (product_subtotal+product_margin_amount -
                                        total_product_discount_price) * quantity
                total_item_discount += (total_product_discount_price * quantity)
                total_item_margin += (product_margin_amount * quantity)

        product_total = {'sub_total': subtotal_unit_price, 'item_margin': total_item_margin,
                         'total': subtotal_unit_price, 'item_discount': total_item_discount, 'discount': 0}
        return product_total

    def get_grand_total(self, total, tax, shipping):
        tax_amount = ((float(total)+float(shipping)) * float(tax)) / 100
        grand_total = float(total)+float(tax_amount)+float(shipping)
        grand_total = round(grand_total, 2)
        tax_amount = round(tax_amount, 2)
        return grand_total, tax_amount

    def calculate_price_unit_type(self, specialprice, product_price, unit_type):
        if unit_type == PRODUCT_MARGIN_PERC_UNIT:
            total_amount = (float(specialprice) * float(product_price))/100
        else:
            total_amount = float(specialprice)
        return total_amount

    def get_customer_address(self, customer_address_id):
        customer_address = CustomerAddresses.objects.filter(
            id=customer_address_id).first()
        return customer_address

    def get_ref_number(self):
        new_ref_number = create_new_ref_number()
        return new_ref_number

    def get_tax_vat(self):
        get_tax_vat = Settings.objects.filter(key=self.tax_vat).first()
        if get_tax_vat is None:
            return 13
        else:
            return get_tax_vat.value

    def create_order_detail(self, order_id, order_recurrence, grocery_product_list):
        for grocery_product in grocery_product_list:
            product = grocery_product.product
            quantity = self.total_product_qty_exist(
                product, float(grocery_product.product_qty))
            if quantity:
                self.create_product(
                    order_id, grocery_product.product_qty, product)
        return 1

    def create_product(self, order_id, pro_quantity, product):
        sku = product.SKU
        product_name = product.name
        price = product.price

        item_margin = product.wayrem_margin

        if product.discount is None:
            discount_price = 0
        else:
            discount_price = product.discount

        if item_margin is None:
            product_margin = 0
            total_price = product.price + 0
        else:
            product_margin = self.calculate_price_unit_type(
                item_margin, product.price, product.margin_unit)
            total_price = float(product.price)+float(product_margin)
        total_product_discount = self.calculate_price_unit_type(
            discount_price, total_price, product.dis_abs_percent)
        #total_discount =float(total_product_discount) * float(pro_quantity)
        total_discount = float(total_product_discount)
        discount = round(total_discount, 2)
        quantity = pro_quantity
        product_id = product.id
        order_details_dic = {'sku': sku, 'product_name': product_name, 'price': price, 'item_margin': product_margin,
                             'discount': discount, 'quantity': quantity, 'order_id': order_id, 'product_id': product_id}

        od = OrderDetails(**order_details_dic)
        od.save()

    def get_grocery_product(self, order_recurrence):
        grocery_id = order_recurrence.grocery_id
        grocery_products = GroceryProducts.objects.filter(grocery=grocery_id)
        return grocery_products

    def generate_invoice(self):
        total_rows = OrderTransactions.objects.count()
        return total_rows + self.invoice_default

    def create_order_transactions(self, order_id, order_recurrence):
        user_id = 1
        invoices_id = self.generate_invoice()
        code = "code"
        order_type = 25
        created_at = datetime.now()
        updated_at = datetime.now()
        content = ""
        order_id = order_id
        payment_mode_id = 10
        payment_status_id = 6
        order_transactions_dic = {'user_id': user_id, 'invoices_id': invoices_id, 'code': code, 'order_type': order_type, 'created_at': created_at,
                                  'updated_at': updated_at, 'content': content, 'order_id': order_id, 'payment_mode_id': payment_mode_id, 'payment_status_id': payment_status_id}

        order_tran = OrderTransactions(**order_transactions_dic)
        order_tran.save()
        return 1
