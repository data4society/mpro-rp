#!/usr/bin/env bash
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install rabbitmq-server
mkdir ~/messaging
cd ~/messaging
sudo virtualenv -p /usr/bin/python3 --no-site-packages mprorpenv
sudo source mprorpenv/bin/activate
sudo pip3 install celery
sudo export C_FORCE_ROOT="true"
