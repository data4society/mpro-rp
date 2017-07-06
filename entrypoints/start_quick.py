"""start script for test learning with test server"""
import sys
sys.path.insert(0, '..')
from mprorp.ner.quick_start import quick_start_pe

if __name__ == '__main__':
    print("STARTING quick_start.py")
    quick_start_pe()
    print("quick_start.py COMPLETE")