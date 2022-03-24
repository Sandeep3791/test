from wayrem_admin.loginext.liberary.api_base import ApiBase
from wayrem_admin.loginext.liberary.order import Order
from wayrem_admin.models_orders import Orders, ShippingLoginextNotification
from wayrem_admin.models_recurrence import ForecastJobtype, ForecastProduct, GroceryProducts, ForecastProduct
from wayrem_admin.models import Settings
from wayrem_admin.utils.constants import *
from datetime import timedelta, date, datetime
from django.db.models import Sum, F


class ProductForecastLiberary:
    def __init__(self):
        self.DELIVERY_SPAN = self.get_setting_value(DELIVERY_SPAN)
        self.FORECAST_PRODUCT_THRESHOLD = self.get_setting_value(
            FORECAST_PRODUCT_THRESHOLD)
        self.FORECAST_PREVIOUS_RECORD_DELETE = FORECAST_PREVIOUS_RECORD_DELETE

    def get_setting_value(self, key):
        get_setting = Settings.objects.filter(key=key).first()
        if get_setting is None:
            return FORECAST_DEFAULT_VALUE
        else:
            try:
                return int(get_setting.value)
            except ValueError:
                print("NOT A INTEGER")
                return FORECAST_DEFAULT_VALUE

    def process_forecast_product(self):
        try:
            next_date_dict = self.get_job_type()
            for next_date_key, next_date_value in next_date_dict.items():
                get_product_quantity = self.get_grocery_products(
                    next_date_value)
                self.forecast_product(next_date_key, get_product_quantity)
            self.delete_productforecast()  # deleted product
            return 1
        except:
            print('Forecast is not executed')

    def delete_productforecast(self):
        previous_date = datetime.today() - timedelta(days=self.FORECAST_PREVIOUS_RECORD_DELETE)
        ForecastProduct.objects.filter(created_at__lte=previous_date).delete()
        return 1

    def forecast_product(self, jobtype, get_product_quantity_dic):
        if get_product_quantity_dic:
            for get_product_quantity in get_product_quantity_dic:
                product_id = get_product_quantity['product']
                forecast_quantity = get_product_quantity['total_product_qty']
                onhand_stock = get_product_quantity['onhand']
                outofstock_product = get_product_quantity['outofstock']
                stock = onhand_stock-outofstock_product
                needed_stock_purchase = self.product_needed(
                    stock, forecast_quantity, onhand_stock, outofstock_product)
                current_datetime = datetime.now()
                if stock >= 0:
                    check_stock = stock
                else:
                    check_stock = 0
                forecast_product_dic = {'forecast_jobtype_id': jobtype, 'product_id': product_id, 'stock': check_stock,
                                        'forecast_quantity': forecast_quantity, 'needed_stock_purchase': needed_stock_purchase, 'created_at': current_datetime}
                self.insert_forecast_product(forecast_product_dic)
        return 1

    def insert_forecast_product(self, forecast_product_dic):
        # check whether product exist for today date or not
        self.check_forecast_exist(forecast_product_dic)
        fp = ForecastProduct(**forecast_product_dic)
        fp.save()
        return 1

    def check_forecast_exist(self, forecast_product_dic):
        jobtype = forecast_product_dic['forecast_jobtype_id']
        product_id = forecast_product_dic['product_id']
        today = date.today()
        start_date_time = today.strftime("%Y-%m-%d 00:00:00")
        last_date_time = today.strftime("%Y-%m-%d 23:59:59")
        is_forcast_product = ForecastProduct.objects.values('id').filter(
            forecast_jobtype_id=jobtype, product_id=product_id, created_at__gte=start_date_time, created_at__lte=last_date_time).first()
        if is_forcast_product is None:
            return forecast_product_dic
        else:
            forecast_product_dic['id'] = is_forcast_product['id']
            return forecast_product_dic

    def product_needed(self, stock, forecast_quantity, onhand_stock, outofstock_product):
        needed_quantity = stock-forecast_quantity
        if needed_quantity >= outofstock_product:
            if needed_quantity >= self.FORECAST_PRODUCT_THRESHOLD:
                return 0
            else:
                needed_qty = self.FORECAST_PRODUCT_THRESHOLD-needed_quantity
                return needed_qty

        if needed_quantity < outofstock_product:
            needed_stock_purchase = forecast_quantity + self.FORECAST_PRODUCT_THRESHOLD
            return needed_stock_purchase

    def get_grocery_products(self, next_date_value):
        get_grocery_products = GroceryProducts.objects.annotate(total_product_qty=Sum('product_qty'), onhand=F('product__inventory_onhand'), outofstock=F('product__outofstock_threshold')).values(
            'product', 'onhand', 'total_product_qty', 'outofstock').filter(recurrence_nextdate__gte=next_date_value['start_date'], recurrence_nextdate__lte=next_date_value['next_date'])
        get_grocery_products.query.group_by = [('product')]
        return get_grocery_products

    def get_job_type(self):
        jobtype = {}
        job_type_dic = ForecastJobtype.objects.filter(status=1)
        for job_type in job_type_dic:
            no_of_days = job_type.no_of_days
            total_days = no_of_days+self.DELIVERY_SPAN
            next_date = date.today() + timedelta(days=total_days)
            jobtype[no_of_days] = {
                'start_date': date.today(), 'next_date': next_date}
        return jobtype
