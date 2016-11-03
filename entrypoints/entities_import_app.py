"""start script for mass themization"""
import sys
sys.path.insert(0, '..')
from mprorp.data.kladr import import_kladr

if __name__ == '__main__':
    print("STARTING ENTITIES IMPORT")
    import_kladr()
    print("ENTITIES IMPORTCOMPLETE")
