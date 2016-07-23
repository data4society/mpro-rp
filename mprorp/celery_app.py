"""start script for celery based running"""
from celery import Celery
import mprorp.celeryconfig as celeryconfig

# create Celery instance and load config
print("STARTING CELERY APP")
app = Celery('mprorp',
             broker='amqp://',
             # backend='amqp://',
             )
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()
