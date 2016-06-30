#!/usr/bin/env bash
# update repositories information
sudo apt-get update
#sudo apt-get -y upgrade
# install some including pip3 and nosetests3
sudo apt-get -y install python3-dev libpq-dev mc python3-pip python3-all-dev python3-nose python3-lxml
# install project requirements
pip3 install -r requirements.txt
# install tensorflow
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.9.0rc0-cp34-cp34m-linux_x86_64.whl
sudo pip3 install --upgrade $TF_BINARY_URL