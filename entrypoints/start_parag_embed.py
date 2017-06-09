"""start script for test learning with test server"""
import sys
sys.path.insert(0, '..')
from mprorp.ner.paragraph_embedding import start

if __name__ == '__main__':
    print("STARTING paragraph_embedding.py")
    start()
    print("paragraph_embedding.py COMPLETE")