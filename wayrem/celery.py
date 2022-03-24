from celery.schedules import crontab
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wayrem.settings')

app = Celery('wayrem')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'import-images-every-5min': {
        'task': 'wayrem_admin.tasks.prod_img',
        'schedule': crontab(minute='*/5'),
        # 'args': (9),
    },
    'forecasting_product_24hrs': {
        'task': 'wayrem_admin.tasks.forecasts_product',
        'schedule': crontab(hour='*/24'),
        # 'args': (9),
    },
    'product_recursion_24hrs': {
        'task': 'wayrem_admin.tasks.product_recursion',
        'schedule': crontab(hour='*/24'),
        # 'args': (9),
    },
}
# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls test('hello') every 10 seconds.
#     sender.add_periodic_task(0.1, test.s('hello'), name='add every 10')

#     # Calls test('world') every 30 seconds
#     sender.add_periodic_task(1.0, test.s('world'), expires=10)

#     # Executes every Monday morning at 7:30 a.m.
#     sender.add_periodic_task(
#         crontab(hour=7, minute=30, day_of_week=1),
#         test.s('Happy Mondays!'),
#     )


# @app.task
# def test(arg):
#     print(arg)
