#!/usr/bin/env bash
useradd mprorp -m
passwd mprorp #set pass
apt-get update
apt-get -y upgrade
dpkg-reconfigure tzdata
apt-get -y install mc python-virtualenv rabbitmq-server python3-pip libpq-dev nginx
apt-get -y build-dep python3-lxml


su mprorp
virtualenv -p /usr/bin/python3 --no-site-packages ~/mprorpenv
cd ~
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
cp /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.sample.py /home/mprorp/local_settings.py
# update local config
cp /home/mprorp/local_settings.py /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.py


su - #input root pass
sh /home/mprorp/mpro-rp-dev/scripts/tomita.sh /home/mprorp
chown -R mprorp:mprorp /home/mprorp
cp /home/mprorp/mpro-rp-dev/server/flower_nginx /etc/nginx/sites-available/flower
ln -s /etc/nginx/sites-available/flower /etc/nginx/sites-enabled/flower
rm /etc/nginx/sites-enabled/default
service nginx reload
cp /home/mprorp/mpro-rp-dev/server/flowerd_init /etc/init.d/flowerd
cp /home/mprorp/mpro-rp-dev/server/celeryd_init /etc/init.d/celeryd
chmod 755 /etc/init.d/flowerd
chmod 755 /etc/init.d/celeryd
cp /home/mprorp/mpro-rp-dev/server/flowerd_default /etc/default/flowerd
cp /home/mprorp/mpro-rp-dev/server/celeryd_default /etc/default/celeryd
chmod 644 /etc/default/flowerd
chmod 644 /etc/default/celeryd
cp /home/mprorp/mpro-rp-dev/server/renew.sh /home/mprorp
update-rc.d celeryd defaults 90
update-rc.d flowerd defaults 91


su mprorp
source ~/mprorpenv/bin/activate
cd ~/mpro-rp-dev
pip3 install -r requirements.txt
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.9.0rc0-cp34-cp34m-linux_x86_64.whl
pip3 install --upgrade $TF_BINARY_URL
pip3 install flower


