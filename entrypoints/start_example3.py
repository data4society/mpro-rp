"""start script for test learning with test server"""
import sys
sys.path.insert(0, '..')
# from mprorp.ner.examples3 import script_exec
from mprorp.ner.paragraph_embedding_loс import words_to_files



if __name__ == '__main__':
    words_to_files('test', [2,3])
    words_to_files('train', range(4))
    print("STARTING example3.py")
    # script_exec()
    print("example3.py COMPLETE")