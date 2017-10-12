"""celery config"""

import sys
import os
# these files contain celery tasks:
CELERY_INCLUDE = ['mprorp.controller.start', 'mprorp.controller.logic']
# to using server time:
CELERY_ENABLE_UTC = False

if sys.argv[0].split("/")[-1] == 'times.py':
    CELERY_ALWAYS_EAGER = True
    CELERYD_TASK_TIME_LIMIT = 600
    CELERYD_TASK_SOFT_TIME_LIMIT = 550
else:
    CELERYD_TASK_TIME_LIMIT = os.environ['CELERYD_TASK_TIME_LIMIT']
    CELERYD_TASK_SOFT_TIME_LIMIT = os.environ['CELERYD_TASK_SOFT_TIME_LIMIT']
    # number of parallel processes:
    CELERYD_CONCURRENCY = os.environ['CELERYD_CONCURRENCY']
    CELERY_TIMEZONE = os.environ['CELERY_TIMEZONE']
