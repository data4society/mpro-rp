"""start script for celery based running"""
from celery import Celery
import mprorp.config.fastart_celeryconfig as celeryconfig
import sys


print("STARTING CELERY APP")

# create Celery instance and load config
app = Celery('mprorp',
                 broker='amqp://',
                 # backend='amqp://',
                 )
app.config_from_object(celeryconfig)

if "--detach" not in sys.argv:
    pass
print("STARTING CELERY APP COMPLETE")

if __name__ == '__main__':
    pass
