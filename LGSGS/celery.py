import os
from celery import Celery
from django.conf import settings

# set the default Django settings_old module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LGSGS.settings')

app = Celery('LGSGS')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

interval = settings.UPDT_INTERVAL * 60

app.conf.beat_schedule = {
    'update_prices-30-minutes': {
        'task': 'assets.tasks.update_prices_task',
        'schedule': interval
    },
}
app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
