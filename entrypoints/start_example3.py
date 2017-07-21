"""start script for test learning with test server"""
import sys
sys.path.insert(0, '..')
from mprorp.ner.examples3 import script_exec
from mprorp.ner.paragraph_embedding_local import words_to_file



if __name__ == '__main__':
    exit()
    words_to_file()
    print("STARTING example3.py")
    script_exec()
    print("example3.py COMPLETE")