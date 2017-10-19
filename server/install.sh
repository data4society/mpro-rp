#!/bin/bash
SERVER_TIMEZONE="Europe/Moscow"
MPRORP_USER_PASS="123"
POSTGRES_USER_PASS="123"
POSTGRESMPRO_USER_PASS="123"
POSTGRESMPRO_BASE_USER_PASS="123"
FASTART_SERVER="11.12.13.14"
FASTART_BASE="postgres_mpro"
FASTART_BASE_USER_PASS="123"

#time in seconds to block process
CELERYD_TASK_SOFT_TIME_LIMIT="55"
#time in seconds to hard block process
CELERYD_TASK_TIME_LIMIT="60"
#number of parallel processes
CELERYD_CONCURRENCY="4"
#log levels
CELERY_LOG_LEVEL="DEBUG"
FLOWER_LOG_LEVEL="INFO"
#period to start checking sources
CELERYBEAT_PERIOD="30"
#number of tasks to show in flower
FLOWER_MAX_TASKS="15000"
#user and pass for flower access
FLOWER_USER_PASS="user:123"

SWAP="4G"


timedatectl set-timezone $SERVER_TIMEZONE
useradd mprorp -m
echo "mprorp:$MPRORP_USER_PASS" | chpasswd
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
apt-get update
apt-get -y upgrade
apt-get -y install mc git python-virtualenv rabbitmq-server python3-pip libpq-dev nginx libblas-dev liblapack-dev libatlas-base-dev gfortran postgresql postgresql-contrib
apt-get -y build-dep python3-lxml

echo "postgres:$POSTGRES_USER_PASS" | chpasswd
useradd postgres_mpro -m
echo "postgres_mpro:$POSTGRESMPRO_USER_PASS" | chpasswd
mkdir /home/postgres
chown postgres:postgres /home/postgres
cd /home/postgres
sudo -u postgres psql -c "CREATE USER postgres_mpro WITH PASSWORD '$POSTGRESMPRO_BASE_USER_PASS';"
sudo -u postgres psql -c "CREATE DATABASE postgres_mpro OWNER postgres_mpro;"
sudo -u postgres psql -U postgres -d postgres_mpro -c 'CREATE EXTENSION "uuid-ossp";'
pg_version=$(pg_config --version | egrep -o '[0-9]{1,}\.[0-9]{1,}')
echo 'host    all    all    0.0.0.0/0    md5' >> /etc/postgresql/$pg_version/main/pg_hba.conf
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/$pg_version/main/postgresql.conf
service postgresql restart

su -c 'mkdir /home/mprorp/models' - mprorp
su -c 'mkdir /home/mprorp/weights' - mprorp
su -c 'virtualenv -p /usr/bin/python3 --no-site-packages ~/mprorpenv' - mprorp
su -c 'cd ~;git clone -b dev --single-branch https://github.com/data4society/mpro-rp.git;mv ~/mpro-rp ~/mpro-rp-dev' - mprorp
su -c 'cp /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.sample.py /home/mprorp/local_settings.py' - mprorp
sed -i "s/maindb_connection = ''/maindb_connection = 'postgresql:\/\/postgres_mpro:$POSTGRESMPRO_BASE_USER_PASS@localhost\/postgres_mpro'/g" /home/mprorp/local_settings.py
sed -i "s/fastart_connection = ''/fastart_connection = 'postgresql:\/\/postgres_mpro:$FASTART_BASE_USER_PASS@$FASTART_SERVER\/$FASTART_BASE'/g" /home/mprorp/local_settings.py
su -c 'cp /home/mprorp/local_settings.py /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.py' - mprorp
su -c 'cp /home/mprorp/mpro-rp-dev/mprorp/config/app.sample.json /home/mprorp/app.json' - mprorp
su -c 'cd ~/mpro-rp-dev; source ~/mprorpenv/bin/activate; pip3 install pip --upgrade; pip3 install -r requirements.txt; pip3 install flower' - mprorp

sh /home/mprorp/mpro-rp-dev/scripts/tomita.sh /home/mprorp
chown -R mprorp:mprorp /home/mprorp
# put nginx conf for flower (celery monitoring tool). We'll can see it by server ip:
# http://xxx.xxx.xxx.xxx/ - flower path
# http://xxx.xxx.xxx.xxx/celery_log.txt - celery log path
cp /home/mprorp/mpro-rp-dev/server/flower_nginx /etc/nginx/sites-available/flower
ln -s /etc/nginx/sites-available/flower /etc/nginx/sites-enabled/flower
rm /etc/nginx/sites-enabled/default
service nginx reload
# creating flower, celerybeat, celery and fastart  daemons
cp /home/mprorp/mpro-rp-dev/server/celeryd.conf /etc/init/celeryd.conf
cp /home/mprorp/mpro-rp-dev/server/celerybeat.conf /etc/init/celerybeat.conf
cp /home/mprorp/mpro-rp-dev/server/flower.conf /etc/init/flower.conf
cp /home/mprorp/mpro-rp-dev/server/fastart.conf /etc/init/fastart.conf
cp /home/mprorp/mpro-rp-dev/server/fastart_flask.conf /etc/init/fastart_flask.conf
sed -i "s/CELERY_LOG_LEVEL=\"DEBUG\"/CELERY_LOG_LEVEL=\"$CELERY_LOG_LEVEL\"/g" /etc/init/celeryd.conf
sed -i "s/CELERYD_TASK_TIME_LIMIT=60/CELERYD_TASK_TIME_LIMIT=$CELERYD_TASK_TIME_LIMIT/g" /etc/init/celeryd.conf
sed -i "s/CELERYD_TASK_SOFT_TIME_LIMIT=55/CELERYD_TASK_SOFT_TIME_LIMIT=$CELERYD_TASK_SOFT_TIME_LIMIT/g" /etc/init/celeryd.conf
sed -i "s/CELERYD_CONCURRENCY=4/CELERYD_CONCURRENCY=$CELERYD_CONCURRENCY/g" /etc/init/celeryd.conf
sed -i "s/CELERY_TIMEZONE=\"Europe\/Moscow\"/CELERY_TIMEZONE=\"${SERVER_TIMEZONE/\//\\/}\"/g" /etc/init/celeryd.conf
sed -i "s/CELERY_TIMEZONE=\"Europe\/Moscow\"/CELERY_TIMEZONE=\"${SERVER_TIMEZONE/\//\\/}\"/g" /etc/init/celerybeat.conf
sed -i "s/CELERYBEAT_PERIOD=30/CELERYBEAT_PERIOD=$CELERYBEAT_PERIOD/g" /etc/init/celerybeat.conf
sed -i "s/CELERY_LOG_LEVEL=\"DEBUG\"/CELERY_LOG_LEVEL=\"$CELERY_LOG_LEVEL\"/g" /etc/init/celerybeat.conf
sed -i "s/FLOWER_TIMEZONE=\"Europe\/Moscow\"/FLOWER_TIMEZONE=\"${SERVER_TIMEZONE/\//\\/}\"/g" /etc/init/flower.conf
sed -i "s/FLOWER_LOG_LEVEL=\"INFO\"/FLOWER_LOG_LEVEL=\"$FLOWER_LOG_LEVEL\"/g" /etc/init/flower.conf
sed -i "s/FLOWER_MAX_TASKS=15000/FLOWER_MAX_TASKS=$FLOWER_MAX_TASKS/g" /etc/init/flower.conf
sed -i "s/FLOWER_BASIC_AUTH=\"\"/FLOWER_BASIC_AUTH=\"$FLOWER_USER_PASS\"/g" /etc/init/flower.conf
chmod 644 /etc/init/celeryd.conf
chmod 644 /etc/init/celerybeat.conf
chmod 644 /etc/init/flower.conf
chmod 644 /etc/init/fastart.conf
# update init configs
# copy renew script to not renewing directory
cp /home/mprorp/mpro-rp-dev/server/renew.sh /home/mprorp
# create alias
echo "alias renew='bash /home/mprorp/renew.sh'" >> ~/.bashrc

#create swap
fallocate -l $SWAP /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile    none    swap    sw    0    0' >> /etc/fstab
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
sysctl vm.swappiness=10
sysctl vm.vfs_cache_pressure=50


# run renew script:
# renew or renew skip_time_test
echo "fin"
