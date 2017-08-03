# setup
`wget https://github.com/data4society/mpro-rp/raw/dev/server/install.sh`

`chmod +x install.sh`

edit constants in install.sh and run it:

`bash install.sh`

edit /home/mprorp/app.json and start mprorp by command:

`start celeryd`

# mpro-rp
regular processes for mpro

testing celery:
su mprorp
cd ~/mpro-rp-dev
source ~/mprorpenv/bin/activate
celery multi start w1 --loglevel=INFO -B --app=mprorp.celery_app:app
run locally logic.py and celery_app.py