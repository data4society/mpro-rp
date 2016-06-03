from __future__ import absolute_import
from celery import Celery
from datetime import timedelta
import mprorp.celeryconfig as celeryconfig

app = Celery('mprorp',
             broker='amqp://',
             backend='amqp://',
             )
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()