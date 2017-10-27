"""celery config"""

from datetime import timedelta
import os
# we have one shedule-task:
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
# CELERY_TIMEZONE = 'UTC'
