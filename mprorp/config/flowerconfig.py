"""celery config"""

import os
broker_url = os.environ['FLOWER_BROKER_URL']

max_tasks = os.environ['FLOWER_MAX_TASKS']
# to using server time:
enable_utc = False
timezone = os.environ['FLOWER_TIMEZONE']
# CELERY_TIMEZONE = 'UTC'
print(os.environ['FLOWER_LOG_FILE_PREFIX'])

