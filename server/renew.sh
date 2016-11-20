#!/usr/bin/env bash
# script for renewing project code base and restart celery based application
# code renewing from dev branch!
cd /home/mprorp
#C_FAKEFORK=1 sh -x /etc/init.d/celeryd stop
/etc/init.d/celeryd stop
/etc/init.d/celeryd status
rm -r mpro-rp-dev
rm dev.zip
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
cp /home/mprorp/local_settings.py /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.py
cp /home/mprorp/app.json /home/mprorp/mpro-rp-dev/mprorp/config/app.json
chown -R mprorp:mprorp /home/mprorp
#C_FAKEFORK=1 sh -x /etc/init.d/celeryd start
#C_FAKEFORK=1 sh -x /etc/init.d/celeryd restart
/etc/init.d/celeryd start
echo "Renew code and restart system complete!"