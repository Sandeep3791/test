
from celery import shared_task
from wayrem_admin.import_prod_img import *
from wayrem_admin.forecasts.product_forecast_liberary import ProductForecastLiberary
from wayrem_admin.forecasts.order_liberary import OrderLiberary
from wayrem_admin.views.credits import credit_reminder


@shared_task(bind=True)
def prod_img(self):
    print("hello world")
    import_image()
    return "Done"


@shared_task(bind=True)
def forecasts_product(self):
    ProductForecastLiberary().process_forecast_product()
    return "Done"


@shared_task(bind=True)
def product_recursion(self):
    OrderLiberary().proccess_order()
    return "Done"


@shared_task(bind=True)
def customer_credit_reminder(self):
    credit_reminder()
    return "Done"
