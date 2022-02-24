from wayrem_admin.forms import warehouse
from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.models_orders import Orders, ShippingLoginextNotification, OrderDetails, OrderTransactions,StatusMaster,ShippingRates,create_new_ref_number
from wayrem_admin.models_recurrence import RecurrentType, RecurrenceGrocery, GroceryMaster, GroceryProducts
from wayrem_admin.models import Settings,CustomerAddresses, Warehouse
from wayrem_admin.utils.constants import *
from datetime import timedelta, date, datetime
from django.db.models import Sum, F
import googlemaps

class OrderLiberary:
    tax_vat=SETTING_VAT
    invoice_default=INVOICE_DEFAULT
    free_shipping_total=FREE_SHIPPING_TOTAL
    paid_shipping_charge=PAID_SHIPPING_CHARGE

    def __init__(self):
        self.recurrence_type = self.recurrent_type()
        self.today_date = date.today()
        self.delivery_order_per_day = self.get_setting_value(
            DELIVERY_ORDER_PER_DAY)
        self.customer_approve_per_day = self.get_setting_value(
            CUSTOMER_APPROVAL_PER_DAY)

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
        total_day = self.today_date + \
            timedelta(days=self.delivery_order_per_day) + \
            timedelta(days=self.customer_approve_per_day)
        return total_day

    def recurrence_grocery(self, get_date):
        recurrence_groccery = RecurrenceGrocery.objects.filter(
            status=1, recurrence_nextdate=get_date)
        return recurrence_groccery

    def create_recurrence_grocery_order(self, recurrence_grocery):
        for rg in recurrence_grocery:
            is_order_created = self.create_order_recurrence(rg)
            if is_order_created:
                self.update_recurrence_groccery(rg) # update nextdate
            

    def update_recurrence_groccery(self, rg):
        no_of_days = rg.recurrenttype.value
        no_of_days =int(no_of_days)
        current_date_next=datetime.strptime(rg.recurrence_nextdate, "%Y-%m-%d").date()
        re_date = current_date_next + timedelta(days=no_of_days)
        RecurrenceGrocery.objects.filter(id=rg.id).update(recurrence_nextdate=re_date,updated_at=datetime.now())
        self.update_grocery_products(rg.grocery_id,re_date)
       
        return 1

    def update_grocery_products(self,grocery_id,next_date):
        groc_product=GroceryProducts.objects.filter(grocery_id=grocery_id)
        for groc_products in groc_product:
            groc_products.recurrence_nextdate=next_date
            groc_products.save()
        return 1

    def create_order_recurrence(self, order_recurrence):
        grocery_product_list = self.get_grocery_product(order_recurrence)
        order_id=self.create_order(order_recurrence,grocery_product_list)

        if order_id:
            self.create_order_detail(order_id, order_recurrence,grocery_product_list)
            self.create_order_transactions(order_id,order_recurrence)
        return order_id
    
    def create_order(self,order_recurrence,grocery_product_list):
        try:
            customer_id=order_recurrence.customer.id
            customer_address=self.get_customer_address(customer_id)
            ref_number = self.get_ref_number()
            tax_vat = self.get_tax_vat()
            product_total=self.product_total(grocery_product_list)
            sub_total=round(product_total['sub_total'],2)
            item_margin=round(product_total['item_margin'],2)
            total=round(product_total['total'],2)

            if customer_address is None:
                order_lat=order_recurrence.customer.billlingAddress_Latitude
                order_long=order_recurrence.customer.billingAddress_longitude
            else:
                order_lat=customer_address.deliveryaddress_latitude
                order_long=customer_address.deliveryaddress_longitude
            
            #shipping = self.get_shipping_value(order_lat,order_long)
            shipping = self.get_shipping_value(total)
            promo = 0
            item_discount = product_total['item_discount']
            discount = round(product_total['discount'],2)
            grand_total,tax = self.get_grand_total(total,tax_vat,shipping)

            full_name=customer_address.full_name

            order_ship_name = full_name
            order_ship_address = customer_address.house_no_building_name
            order_ship_building_name = customer_address.road_name_area

            order_ship_landmark = customer_address.landmark
            order_ship_region = customer_address.region
            order_ship_latitude = order_lat
            order_ship_longitude = order_long
            order_billing_name = full_name
            order_billing_address = order_recurrence.customer.delivery_house_no_building_name
            
            order_city = customer_address.town_city
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
            #status = StatusMaster(id=23) on phase 2 this will recurrent pending for approval.
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

    def get_shipping_value(self,total_amount):
        if total_amount > float(self.free_shipping_total):
            return 0
        else:
            paid_shipping_charge=self.get_setting_value(self.paid_shipping_charge)
            return paid_shipping_charge

    def get_shipping_value_old(self,customer_latitude,customer_longitude):
        gmaps = googlemaps.Client(key='AIzaSyCT93vNszQ2b8JQmHqrkDTVJnjVKmHSaTc')
        warehouse=Warehouse.objects.filter(status=1).first()
        
        warehouse_latitude = warehouse.latitude
        warehouse_longitude = warehouse.longitude

        origin_latitude = float(warehouse_latitude)
        origin_longitude = float(warehouse_longitude)
        destination_latitude = float(customer_latitude)
        destination_longitude = float(customer_longitude)
        
        distance = gmaps.distance_matrix([str(origin_latitude) + " " + str(origin_longitude)], [str(
        destination_latitude) + " " + str(destination_longitude)], mode='driving')['rows'][0]['elements'][0]
        
        x = distance.get("distance").get('value')
        y = float(x/1000)
        calculate_price=self.calculate_price_km(y)
        total_shipping_charge=calculate_price * y
        return total_shipping_charge

    def calculate_price_km(self,km):
        km=int(km)
        sr=ShippingRates.objects.filter(from_dest__gte=km,to_dest__lte=km).first()
        if sr is None:
            return DEFAULT_SHIPPING_AMOUNT
        else:
            return sr.price

    def product_total(self,grocery_product_list):
        subtotal_unit_price=0
        product_margin=0
        total_discount=0
        product_total={}
        total_item_discount=0
        for gpl in grocery_product_list:
            quantity=gpl.product_qty
            subtotal_unit_price += (float(gpl.product.price) * float(quantity))
            
            tot_marg_amount=self.calculate_price_unit_type(gpl.product.wayrem_margin,gpl.product.price,gpl.product.margin_unit)
            product_margin += (tot_marg_amount * float(quantity))
            if gpl.product.discount is None:
                discount_price=0
            else:
                total_item_discount +=1
                discount_price=gpl.product.discount            
            total_product_discount=self.calculate_price_unit_type(discount_price,gpl.product.price,gpl.product.dis_abs_percent)
            total_discount +=float(total_product_discount) * float(quantity)

        subtotal= subtotal_unit_price +  product_margin 
        total= (subtotal_unit_price +  product_margin) - total_discount 
        product_total = {'sub_total':subtotal,'item_margin':product_margin,'total':total,'item_discount':total_item_discount,'discount':total_discount}
        return product_total

    def get_grand_total(self,total,tax,shipping):
        tax_amount= (float(total) * float(tax) ) / 100
        grand_total=float(total)+float(tax_amount)+float(shipping)
        grand_total=round(grand_total,2)
        tax_amount=round(tax_amount,2)
        return grand_total,tax_amount

    def calculate_price_unit_type(self,specialprice,product_price,unit_type):
        if unit_type == PRODUCT_MARGIN_PERC_UNIT:
            total_amount=(float(specialprice) * float(product_price))/100
        else:
            total_amount=float(specialprice)
        return total_amount

    def get_customer_address(self,customer_id):
        customer_address=CustomerAddresses.objects.filter(customer_id=customer_id,is_default=1).first()
        return customer_address

    def get_ref_number(self):
        new_ref_number=create_new_ref_number()
        return new_ref_number

    def get_tax_vat(self):
        get_tax_vat=Settings.objects.filter(key=self.tax_vat).first()
        if get_tax_vat is None:
            return 13
        else:
            return get_tax_vat.value


    def create_order_detail(self, order_id, order_recurrence,grocery_product_list):
        for grocery_product in grocery_product_list:
            product = grocery_product.product
            self.create_product(order_id,grocery_product.product_qty,product)
        return 1

    def create_product(self,order_id,pro_quantity ,product):
        sku = product.SKU
        product_name = product.name
        price = product.price
        item_margin = product.wayrem_margin
        if  product.discount is None:
            discount_price=0
        else:
            discount_price=product.discount            
        total_product_discount=self.calculate_price_unit_type(discount_price,product.price,product.dis_abs_percent)
        total_discount =float(total_product_discount) * float(pro_quantity)
        discount =round(total_discount,2)
        quantity = pro_quantity
        product_id = product.id
        order_details_dic = {'sku': sku, 'product_name': product_name, 'price': price, 'item_margin': item_margin,
                             'discount': discount, 'quantity': quantity, 'order_id': order_id, 'product_id': product_id}
        od = OrderDetails(**order_details_dic)
        od.save()

    def get_grocery_product(self, order_recurrence):
        grocery_id = order_recurrence.grocery_id
        grocery_products = GroceryProducts.objects.filter(grocery=grocery_id)
        return grocery_products

    def generate_invoice(self):
        total_rows=OrderTransactions.objects.count()
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
