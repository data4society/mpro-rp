#!/usr/bin/env bash
useradd mprorp -m
passwd mprorp #set pass
apt-get update
apt-get -y upgrade
apt-get -y install mc python-virtualenv rabbitmq-server python3-pip libpq-dev nginx
apt-get -y build-dep python3-lxml


su mprorp
virtualenv -p /usr/bin/python3 --no-site-packages ~/mprorpenv
cd ~
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
sh ~/mpro-rp-dev/scripts/tomita.sh
cp /home/mprorp/mpro-rp-dev/mprorp/config/local-settings.sample.py /home/mprorp/mpro-rp-dev/mprorp/config/local-settings.py
# update local config
cp /home/mprorp/mpro-rp-dev/mprorp/config/local-settings.py /home/mprorp/


su - #input root pass
sh /home/mprorp/mpro-rp-dev/scripts/tomita.sh /home/mprorp
mkdir /var/www
mkdir /var/www/mprorp
cp /home/mprorp/mpro-rp-dev/scripts/flower /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/flower /etc/nginx/sites-enabled/flower


su mprorp
source ~/mprorpenv/bin/activate
cd ~/mpro-rp-dev
pip3 install -r requirements.txt
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.9.0rc0-cp34-cp34m-linux_x86_64.whl
pip3 install --upgrade $TF_BINARY_URL
pip3 install flower
