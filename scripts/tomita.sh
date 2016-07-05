#!/usr/bin/env bash
cd $1
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
cd bin
sudo wget https://github.com/yandex/tomita-parser/releases/download/v1.0/libmystem_c_binding.so.linux_x64.zip
sudo unzip libmystem_c_binding.so.linux_x64.zip