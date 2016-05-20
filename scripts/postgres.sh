#!/usr/bin/env bash
sudo apt-get -y install postgresql postgresql-contrib
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'password';"
sudo -u postgres psql -U postgres -d postgres -c 'CREATE EXTENSION "uuid-ossp";'