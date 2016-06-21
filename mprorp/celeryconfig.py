from datetime import timedelta
CELERY_INCLUDE = ['mprorp.controller.start','mprorp.controller.logic',
                  'mprorp.crawler.vk','mprorp.crawler.google_news']
CELERYBEAT_SCHEDULE = {
                          'add-every-30-seconds': {
                              'task': 'mprorp.controller.start.check_sources',
                              'schedule': timedelta(seconds=30),
                          },
                      }
CELERY_TIMEZONE = 'UTC'
CELERYD_CONCURRENCY = 1
CELERYD_FORCE_EXECV = True