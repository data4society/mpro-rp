from datetime import timedelta
from celery.schedules import crontab
CELERY_INCLUDE = ['mprorp.controller.start']
CELERYBEAT_SCHEDULE = {
                          'add-every-5-seconds': {
                              'task': 'mprorp.controller.tasks.add',
                              'schedule': timedelta(seconds=10),
                          },
                      }
CELERY_TIMEZONE = 'UTC'