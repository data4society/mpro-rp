"""start script for NER learning"""
import sys
sys.path.insert(0, '..')
from mprorp.ner.NER import NER_person_learning

if __name__ == '__main__':
    print("STARTING NER LEARNING")
    NER_person_learning()
    print("LEARNING COMPLETE")