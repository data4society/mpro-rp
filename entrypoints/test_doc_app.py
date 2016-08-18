"""start script for NER learning"""
import sys
sys.path.insert(0, '..')
from mprorp.controller.logic import regular_rubrication

if __name__ == '__main__':
    print("STARTING TESTING DOC")
    regular_rubrication('7e2904bf-ef62-4bab-b67f-338aa4c8906a', 102, 2001)
    print("TESTING DOC COMPLETE")
