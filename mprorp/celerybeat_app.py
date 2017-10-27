"""start script for celery based running"""
from celery import Celery
import mprorp.config.celerybeatconfig as celerybeatconfig

app = Celery('mprorp', broker='redis://')
app.config_from_object(celerybeatconfig)
# create Celery instance and load config
print("STARTING CELERYBEAT APP COMPLETE")

if __name__ == '__main__':
    pass;
    #app.start()
