#!/usr/bin/env bash
# base setup script for vagrant and travis
# update repositories information
sudo apt-get update
#sudo apt-get -y upgrade
# install some libs
sudo apt-get -y install libpq-dev mc python3-pip python3-nose
sudo apt-get -y build-dep python3-lxml
sudo apt-get -y libblas-dev liblapack-dev libatlas-base-dev gfortran
# install project requirements
sudo pip3 install -r requirements.txt
# install tensorflow
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.9.0rc0-cp34-cp34m-linux_x86_64.whl
sudo pip3 install --upgrade $TF_BINARY_URL