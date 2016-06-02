#!/usr/bin/env bash
# include repository of postgres
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
sudo apt-get update
# install postgres
sudo apt-get -y install postgresql postgresql-contrib
# set password 'password' for user postgres
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'password';"
# create extension for using uuid generator
sudo -u postgres psql -U postgres -d postgres -c 'CREATE EXTENSION "uuid-ossp";'