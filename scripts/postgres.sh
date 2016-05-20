#!/usr/bin/env bash
sudo apt-get install postgresql
sudo -u postgres psql -U postgres -d postgres -c "alter user postgres with password 'password';"
sudo -u postgres psql -U postgres -d postgres -c "CREATE EXTENSION 'uuid-ossp';"