"""start script for celery based running"""
from celery import Celery
import mprorp.config.flowerconfig as flowerconfig
import os

# create Celery instance and load config
app = Celery('mprorp',
                 broker='amqp://',
                 # backend='amqp://',
                 )
app.config_from_object(flowerconfig)
print("STARTING FLOWER APP COMPLETE")

if __name__ == '__main__':
    pass;
    #app.start()
