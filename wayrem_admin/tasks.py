
from celery import shared_task
from wayrem_admin.import_prod_img import *
from wayrem_admin.forecasts.product_forecast_liberary import ProductForecastLiberary

@shared_task(bind=True)
def prod_img(self):
    print("hello world")
    import_image()
    return "Done"

@shared_task(bind=True)
def forecasts_product(self):
    ProductForecastLiberary().process_forecast_product()
    return "Done"