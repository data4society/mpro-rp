#!/usr/bin/env bash
sudo apt-get update
#sudo apt-get -y upgrade
sudo apt-get -y install python3-dev libpq-dev mc python3-pip
sudo pip3 install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.8.0-cp34-cp34m-linux_x86_64.whl