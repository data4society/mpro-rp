#!/usr/bin/env bash
# script for NER learning
su mprorp
rm -r ~/weights
source ~/mprorpenv/bin/activate
cd ~/mpro-rp-dev
python3 entrypoints/ner_learning_app.py
echo "Learning complete!"