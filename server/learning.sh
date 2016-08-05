#!/usr/bin/env bash
# script for NER learning
/etc/init.d/celeryd stop
su mprorp
rm -r ~/weights
source ~/mprorpenv/bin/activate
cd ~/mpro-rp-dev/entrypoints
python3 ner_learning_app.py
/etc/init.d/celeryd start
echo "Learning complete!"