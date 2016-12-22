# mpro-rp
regular processes for mpro

testing celery:
su mprorp
cd ~/mpro-rp-dev
source ~/mprorpenv/bin/activate
celery multi start w1 --loglevel=INFO -B --app=mprorp.celery_app:app
run locally logic.py and celery_app.py