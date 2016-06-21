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


# celery -A mprorp worker -B --app=mprorp.celery_app:app --logfile=celery_log.txt -l INFO