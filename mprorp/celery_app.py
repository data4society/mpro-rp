"""start script for celery based running"""
from celery import Celery
import mprorp.config.celeryconfig as celeryconfig
import logging

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', filename = u'/home/mprorp/mpro-rp-dev/cel.txt')
root = logging.getLogger()
root.setLevel(logging.DEBUG)

logging.info("start init")
app = Celery('mprorp', broker='redis://')
app.config_from_object(celeryconfig)
logging.info("fin init")

if __name__ == '__main__':
    pass;
    #app.start()
