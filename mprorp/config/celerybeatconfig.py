"""celery config"""

from datetime import timedelta
import os
# we have one shedule-task:
broker_url = os.environ['CELERYD_BROKER_URL']
beat_schedule  = {
                          'resource-checking': {
                              'task': 'mprorp.controller.start.check_sources',
                              'schedule': timedelta(seconds=int(os.environ['CELERYBEAT_PERIOD'])),
                          },
                      }
# to using server time:
enable_utc = False
timezone = os.environ['CELERY_TIMEZONE']
task_default_queue = 'main'
result_expires = None
# CELERY_TIMEZONE = 'UTC'
