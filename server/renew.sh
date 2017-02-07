#!/bin/bash
# script for renewing project code base and restart celery based application
# code renewing from dev branch!
usage ()
{
  echo 'Usage: renew [--skip_time_test] [--skip_restart]'
  exit
}

do_time_test=true
restart=true
while [ "$1" != "" ]; do
    if [ $1 = "--skip_restart" ]; then
        restart=false
    elif [ $1 = "--skip_time_test" ]; then
        do_time_test=false
    else
        usage
    fi
    shift
done
if $restart; then
    stop celeryd
    sleep 3
    status celerybeat
    status flower
fi
cd /home/mprorp
rm -r mpro-rp-dev
rm dev.zip
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
cp /home/mprorp/local_settings.py /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.py
cp /home/mprorp/app.json /home/mprorp/mpro-rp-dev/mprorp/config/app.json
chown -R mprorp:mprorp /home/mprorp
if $do_time_test; then
    su -c 'pm2 stop all' - mpro
    su -c 'cd ~/mpro-rp-dev/local_entrypoints; source ~/mprorpenv/bin/activate; python3 times.py' - mprorp
    su -c 'pm2 start all' - mpro
fi
echo "Renew complete!"
if $restart; then
    start celeryd
    sleep 3
    status celerybeat
    status flower
    echo "Restart complete!"
fi
