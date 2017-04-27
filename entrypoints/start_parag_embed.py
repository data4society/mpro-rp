"""start script for test learning with test server"""
import sys
sys.path.insert(0, '..')
from mprorp.ner.paragraph_embed import start

if __name__ == '__main__':
    print("STARTING paragraph_embed.py")
    start()
    print("paragraph_embed.py COMPLETE")