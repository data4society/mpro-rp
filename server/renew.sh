#!/usr/bin/env bash
su mprorp
cd ~
rm -r mpro-rp-dev
rm dev.zip
wget https://github.com/data4society/mpro-rp/archive/dev.zip
unzip dev.zip
/etc/init.d/celeryd restart