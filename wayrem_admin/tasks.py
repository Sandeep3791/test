
from celery import shared_task
from wayrem_admin.import_prod_img import *


@shared_task(bind=True)
def prod_img(self):
    print("hello world")
    import_image()
    return "Done"
