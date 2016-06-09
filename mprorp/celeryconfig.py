from datetime import timedelta
from celery.schedules import crontab
CELERY_INCLUDE = ['mprorp.controller.start','mprorp.crawler.vk','mprorp.analyzer.rubricator']
CELERYBEAT_SCHEDULE = {
                          'add-every-10-seconds': {
                              'task': 'mprorp.controller.start.check_sources',
                              'schedule': timedelta(seconds=30),
                          },
                      }
CELERY_TIMEZONE = 'UTC'
CELERYD_CONCURRENCY = 1
CELERYD_FORCE_EXECV = True