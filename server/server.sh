#!/usr/bin/env bash
# pseudo shell script for installing mpro-rp project witch celery flower on real Debian server

# create special not super user for running celery based app
useradd mprorp -m
passwd mprorp # set pass
apt-get update
apt-get -y upgrade
dpkg-reconfigure tzdata # change server timezone
apt-get -y install mc python-virtualenv rabbitmq-server python3-pip libpq-dev nginx
apt-get -y build-dep python3-lxml
apt-get -y install libblas-dev liblapack-dev libatlas-base-dev gfortran


# we'll run our app in virtualenv '/home/mprorp/mprorpenv'
su mprorp
virtualenv -p /usr/bin/python3 --no-site-packages ~/mprorpenv
cd ~
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
cp /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.sample.py /home/mprorp/local_settings.py
# update local config at /home/mprorp/local_settings.py with real database connection string
cp /home/mprorp/local_settings.py /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.py
cp /home/mprorp/mpro-rp-dev/mprorp/config/app.sample.json /home/mprorp/app.json
# update application config at /home/mprorp/app.json with real app settings
cp /home/mprorp/app.json /home/mprorp/mpro-rp-dev/mprorp/config/app.json


su - #input root pass
sh /home/mprorp/mpro-rp-dev/scripts/tomita.sh /home/mprorp
chown -R mprorp:mprorp /home/mprorp
# put nginx conf for flower (celery monitoring tool). We'll can see it by server ip:
# http://xxx.xxx.xxx.xxx/ - flower path
# http://xxx.xxx.xxx.xxx/celery_log.txt - celery log path
cp /home/mprorp/mpro-rp-dev/server/flower_nginx /etc/nginx/sites-available/flower
ln -s /etc/nginx/sites-available/flower /etc/nginx/sites-enabled/flower
rm /etc/nginx/sites-enabled/default
#service nginx reload
# creating flower, celerybeat and celery daemons
cp /home/mprorp/mpro-rp-dev/server/celeryd.conf /etc/init/celeryd.conf
cp /home/mprorp/mpro-rp-dev/server/celerybeat.conf /etc/init/celerybeat.conf
cp /home/mprorp/mpro-rp-dev/server/flower.conf /etc/init/flower.conf
chmod 644 /etc/init/celeryd.conf
chmod 644 /etc/init/celerybeat.conf
chmod 644 /etc/init/flower.conf
# update init configs
# copy renew script to not renewing directory
cp /home/mprorp/mpro-rp-dev/server/renew.sh /home/mprorp
echo "alias renew='bash /home/mprorp/renew.sh'" >> ~/.bashrc
# run renew script:
# renew or renew skip_time_test


su mprorp
source ~/mprorpenv/bin/activate
cd ~/mpro-rp-dev
# install requirements and tensorflow
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.9.0rc0-cp34-cp34m-linux_x86_64.whl
pip3 install --upgrade $TF_BINARY_URL
pip3 install -r requirements.txt
pip3 install flower

# for refresh nginx config and start our flower and celery daemons
reboot
