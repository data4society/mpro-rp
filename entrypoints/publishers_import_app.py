"""start script for mass themization"""
import sys
sys.path.insert(0, '..')
from mprorp.data.ya_smi import ya_smi_import
from mprorp.utils import home_dir

if __name__ == '__main__':
    print("STARTING PUBLISHERS IMPORT")
    ya_smi_import(home_dir + '/mpro-rp-dev/mprorp/data/ya_smi/ya_smi.json', home_dir + '/mpro-rp-dev/mprorp/data/ya_smi/out.csv')
    print("PUBLISHERS IMPORT COMPLETE")
