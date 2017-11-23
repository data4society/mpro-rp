"""celery config for fastart"""
import os
# these files contain celery tasks:
include = ['mprorp.fastart.learning_controller', 'mprorp.controller.logic']
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
    },
    'mprorp.controller.logic.regular_calculate_fasttext_embedding': {
        'queue': 'fastart'
    },
    'mprorp.fastart.learning_controller.*': {
        'queue': 'fastart'
    }
}

task_time_limit = os.environ['CELERYD_TASK_TIME_LIMIT']
task_soft_time_limit = os.environ['CELERYD_TASK_SOFT_TIME_LIMIT']
timezone = os.environ['CELERY_TIMEZONE']
