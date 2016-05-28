#!/usr/bin/env bash
# install postgres
sudo apt-get -y install postgresql postgresql-contrib
# set password 'password' for user postgres
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'password';"
# create extension for using uuid generator
sudo -u postgres psql -U postgres -d postgres -c 'CREATE EXTENSION "uuid-ossp";'