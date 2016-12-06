"""celery config"""

from datetime import timedelta
# these files contain celery tasks:
CELERY_INCLUDE = ['mprorp.controller.start', 'mprorp.controller.logic']
# we have one shedule-task:
CELERYBEAT_SCHEDULE = {
                          'resource-checking': {
                              'task': 'mprorp.controller.start.check_sources',
                              'schedule': timedelta(seconds=30),
                          },
                      }
# to using server time:
CELERY_ENABLE_UTC = False
# CELERY_TIMEZONE = 'UTC'
# number of parallel processes:
CELERYD_CONCURRENCY = 8
# for normal working):
CELERYD_FORCE_EXECV = True
CELERYD_TASK_TIME_LIMIT = 60
CELERYD_TASK_SOFT_TIME_LIMIT = 55