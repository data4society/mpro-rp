#!/usr/bin/env bash
# update repositories information
sudo apt-get update
#sudo apt-get -y upgrade
# install some including pip3 and nosetests3
sudo apt-get -y install python3-dev libpq-dev mc python3-pip python3-all-dev python3-nose python3-lxml
# install project requirements
sudo pip3 install -r requirements.txt
# install tensorflow
sudo pip3 install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.8.0-cp34-cp34m-linux_x86_64.whl

cd /home/vagrant
mkdir tomita
cd tomita
sudo apt-get -y install gcc-4.8 g++-4.8 cmake lua5.2 zip
wget https://github.com/yandex/tomita-parser/archive/master.zip
unzip master.zip
cd tomita-parser-master
mkdir build
cd build
sudo cmake ../src/ -DCMAKE_BUILD_TYPE=Release
sudo make
wget https://github.com/yandex/tomita-parser/releases/download/v1.0/libmystem_c_binding.so.linux_x64.zip
unzip libmystem_c_binding.so.linux_x64.zip