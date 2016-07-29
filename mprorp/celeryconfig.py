"""celery config"""

from datetime import timedelta
# these files contain celery tasks:
CELERY_INCLUDE = ['mprorp.controller.start', 'mprorp.controller.logic']
# we have one shedule-task:
CELERYBEAT_SCHEDULE = {
                          'resource-checking': {
                              'task': 'mprorp.controller.start.check_sources',
                              #'task': 'mprorp.controller.start.ner_learning',
                              'schedule': timedelta(seconds=30),
                          },
                      }
# to using server time:
CELERY_ENABLE_UTC = False
# CELERY_TIMEZONE = 'UTC'
# number of parallel processes:
CELERYD_CONCURRENCY = 3
# for normal working):
CELERYD_FORCE_EXECV = True
