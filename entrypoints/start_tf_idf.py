"""start script for test learning with test server"""
import sys
sys.path.insert(0, '..')
from mprorp.ner.create_training_set import do_job

if __name__ == '__main__':
    print("STARTING create_training_set.py")
    do_job()
    print("create_training_set.py COMPLETE")