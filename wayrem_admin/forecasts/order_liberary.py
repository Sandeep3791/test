from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.models_orders import Orders,ShippingLoginextNotification,OrderDetails,OrderTransactions
from wayrem_admin.models_recurrence import RecurrentType,RecurrenceGrocery,GroceryMaster,GroceryProducts
from wayrem_admin.models import Settings
from wayrem_admin.utils.constants import *
from datetime import timedelta, date,datetime
from django.db.models import Sum,F



class OrderLiberary:
    def __init__(self):
        self.recurrence_type=self.recurrent_type()
        self.today_date = date.today()
        self.delivery_order_per_day = self.get_setting_value(DELIVERY_ORDER_PER_DAY)
        self.customer_approve_per_day = self.get_setting_value(CUSTOMER_APPROVAL_PER_DAY)

    def recurrent_type(self):
        recurrence_type=RecurrentType.objects.filter(status=1).order_by('value')
        return recurrence_type

    def proccess_order(self):
        get_date=self.get_filter_data()
        recurrence_grocery=self.recurrence_grocery(get_date)
        if recurrence_grocery:
            self.create_recurrence_grocery_order(recurrence_grocery)

    def get_setting_value(self,keys):
        get_setting=Settings.objects.filter(key=keys).first()
        return int(get_setting.value)

    def get_filter_data(self):
        total_day= self.today_date + timedelta(days=self.delivery_order_per_day)+ timedelta(days=self.customer_approve_per_day)
        return total_day

    def recurrence_grocery(self,get_date):
        recurrence_groccery=RecurrenceGrocery.objects.filter(status=1,recurrence_nextdate=get_date)
        return recurrence_groccery

    def create_recurrence_grocery_order(self,recurrence_grocery):
        for rg in recurrence_grocery:
            is_order_created=self.create_order_recurrence(rg)
            is_order_created=1
            if is_order_created:
                self.update_recurrence_groccery(rg)

    def update_recurrence_groccery(self,rg):
        no_of_days=rg.recurrenttype.value
        re_date=rg.recurrence_nextdate +timedelta(days=no_of_days)+ timedelta(days=self.delivery_order_per_day)+ timedelta(days=self.customer_approve_per_day)
        #RecurrenceGrocery.objects.filter(id=rg.id).update(recurrence_nextdate=re_date,updated_at=datetime.now())
        return 1

    def create_order_recurrence(self,order_recurrence):
        #order_id=self.create_order(order_recurrence)
        order_id=100
        self.create_order_detail(order_id,order_recurrence)
        #self.create_order_transactions(order_id,order_recurrence)
        return order_id


    def create_order(self,order_recurrence):
        ref_number=5
        sub_total=12
        item_discount=1
        item_margin=12
        tax=1
        tax_vat=12
        shipping=12
        total=12
        promo=0
        discount=12
        grand_total=12
        
        order_ship_name=12
        order_ship_address='order_ship_address'
        order_ship_building_name='order_ship_building_name'
        order_ship_landmark="order_ship_landmark"
        order_ship_region="order_ship_region"
        order_ship_latitude="order_ship_latitude"
        order_ship_longitude="order_ship_longitude"
        order_billing_name="order_billing_name"
        order_billing_address="order_billing_address"
        order_city="order_city"
        order_country="order_country"
        order_phone="order_phone"
        order_email="order_email"
        order_date="order_date"
        order_shipped="order_shipped"
        order_tracking_number=None
        content=None
        customer_id=None
        delivery_status=None
        status=None
        order_shipping_response=None
        order_shipping_response=None
        order_type=None

        order_dic={'ref_number':ref_number,'sub_total':sub_total,'item_discount':item_discount,'item_margin':item_margin,'tax':tax,'tax_vat':tax_vat,'shipping':shipping,'total':total,'promo':promo,'discount':discount,'grand_total':grand_total,'order_ship_name':order_ship_name,'order_ship_address':order_ship_address,'order_ship_building_name':order_ship_building_name,'order_ship_landmark':order_ship_landmark,'order_ship_region':order_ship_region,'order_ship_latitude':order_ship_latitude,'order_ship_longitude':order_ship_longitude,'order_billing_name':order_billing_name,
        'order_billing_address':order_billing_address,'order_city':order_city,'order_country':order_country,'order_phone':order_phone,'order_email':order_email,'order_date':order_date,'order_shipped':order_shipped,'order_tracking_number':order_tracking_number,'content':content,'customer_id':customer_id,'delivery_status':delivery_status,'status':status,
        'order_shipping_response':order_shipping_response,'order_type':order_type}
        order_cr=Orders(**order_dic)
        new_order_cr=order_cr.save()
        order_id=new_order_cr.id
        return order_id

    def create_order_detail(self,order_id,order_recurrence):
        grocery_product_list=self.get_grocery_product(order_recurrence)
        for grocery_product in grocery_product_list:
            product=grocery_product.product
            self.create_product(product)            
        return 1

    def create_product(self,product):
        sku='sku'
        product_name='product_name'
        price='price'
        item_margin='item_margin'
        discount='discount'
        quantity='quantity'
        order_id='order_id'
        product_id='product_id'
        order_details_dic={'sku':sku,'product_name':product_name,'price':price,'item_margin':item_margin,'discount':discount,'quantity':quantity,'order_id':order_id,'product_id':product_id}
        od=OrderDetails(**order_details_dic)
        od.save()
        
    def get_grocery_product(self,order_recurrence):
        grocery_id=order_recurrence.grocery_id
        grocery_products=GroceryProducts.objects.filter(grocery=grocery_id)
        return grocery_products

    def  create_order_transactions(self,order_id,order_recurrence):
        user_id=1
        invoices_id="sdsd"
        code="code"
        order_type="order_type"
        created_at="created_at"
        updated_at="updated_at"
        content="content"
        order_id=order_id
        payment_mode_id=""
        payment_status_id=""
        order_transactions_dic={'user_id':user_id,'invoices_id':invoices_id,'code':code,'order_type':order_type,'created_at':created_at,'updated_at':updated_at,'content':content,'order_id':order_id,'payment_mode_id':payment_mode_id,'payment_status_id':payment_status_id}
        order_tran=OrderTransactions(**order_transactions_dic)
        order_tran.save()
        return 1

