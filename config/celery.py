import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.task_default_queue = 'project_queue'
# app.conf.beat_schedule = {
#     'add-every-30-seconds': {
#         'task': 'custom_add',
#         'schedule': 30.0,
#         'args': (16, 16)
#     },
# }


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')