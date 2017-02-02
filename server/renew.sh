#!/usr/bin/env bash
# script for renewing project code base and restart celery based application
# code renewing from dev branch!
cd /home/mprorp
#C_FAKEFORK=1 sh -x /etc/init.d/celeryd stop
/etc/init.d/celerybeat stop
/etc/init.d/celeryd stop
rm -r mpro-rp-dev
rm dev.zip
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
cp /home/mprorp/local_settings.py /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.py
cp /home/mprorp/app.json /home/mprorp/mpro-rp-dev/mprorp/config/app.json
chown -R mprorp:mprorp /home/mprorp
#C_FAKEFORK=1 sh -x /etc/init.d/celeryd start
#C_FAKEFORK=1 sh -x /etc/init.d/celeryd restart
if [ "$1" != "skip_time_test" ]; then
    su -c 'pm2 stop all' - mpro
    su -c 'cd ~/mpro-rp-dev/local_entrypoints; source ~/mprorpenv/bin/activate; python3 times.py' - mprorp
    su -c 'pm2 start all' - mpro
fi
/etc/init.d/celeryd start
/etc/init.d/celerybeat start
echo "Renew code and restart system complete!"