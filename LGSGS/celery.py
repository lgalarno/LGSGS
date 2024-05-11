import os
from celery import Celery

# set the default Django settings_old module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LGSGS.settings')

app = Celery('LGSGS')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_prices-30-minutes': {
        'task': 'assets.tasks.update_prices',
        'schedule': 60.0
    },
}
app.conf.timezone = 'UTC'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
