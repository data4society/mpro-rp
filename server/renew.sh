#!/usr/bin/env bash
su mprorp
cd ~
rm -r mpro-rp-dev
rm dev.zip
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
cp /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.sample.py /home/mprorp/mpro-rp-dev/mprorp/config/local_settings.py
/etc/init.d/celeryd restart