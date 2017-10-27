"""celery config"""

from datetime import timedelta
import sys
import os
# these files contain celery tasks:
include = ['mprorp.controller.start', 'mprorp.controller.logic']
# to using server time:
enable_utc = False
task_default_queue = 'default'

task_routes = {
    'mprorp.controller.start.check_sources': {
        'queue': 'main'
    },
    'mprorp.controller.logic.regular_*_start_parsing': {
        'queue': 'main'
    },
    'mprorp.controller.logic.regular_download_page': {
        'queue': 'network'
    },
    'mprorp.controller.logic.regular_theming': {
        'queue': 'theme'
    }
}


if sys.argv[0].split("/")[-1] == 'times.py':
    always_eager = True
    task_time_limit = 600
    task_soft_time_limit = 550
else:
    task_time_limit = os.environ['CELERYD_TASK_TIME_LIMIT']
    task_soft_time_limit = os.environ['CELERYD_TASK_SOFT_TIME_LIMIT']
    timezone = os.environ['CELERY_TIMEZONE']
