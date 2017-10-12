"""celery config for fastart"""

import os
# these files contain celery tasks:
CELERY_INCLUDE = ['mprorp.fastart.learning_controller']
# to using server time:
CELERY_ENABLE_UTC = False

CELERYD_TASK_TIME_LIMIT = os.environ['CELERYD_TASK_TIME_LIMIT']
CELERYD_TASK_SOFT_TIME_LIMIT = os.environ['CELERYD_TASK_SOFT_TIME_LIMIT']
# number of parallel processes:
CELERYD_CONCURRENCY = os.environ['CELERYD_CONCURRENCY']
CELERY_TIMEZONE = os.environ['CELERY_TIMEZONE']
