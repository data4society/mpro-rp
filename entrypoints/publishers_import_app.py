"""start script for mass themization"""
import sys
sys.path.insert(0, '..')
from mprorp.data.ya_smi import ya_smi_import

if __name__ == '__main__':
    print("STARTING PUBLISHERS IMPORT")
    ya_smi_import()
    print("PUBLISHERS IMPORT COMPLETE")
