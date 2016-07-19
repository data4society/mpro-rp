from datetime import timedelta
CELERY_INCLUDE = ['mprorp.controller.start','mprorp.controller.logic']
CELERYBEAT_SCHEDULE = {
                          'resource-checking': {
                              'task': 'mprorp.controller.start.check_sources',
                              'schedule': timedelta(seconds=30),
                          },
                      }
# CELERY_TIMEZONE = 'UTC'
CELERYD_CONCURRENCY = 1
CELERYD_FORCE_EXECV = True