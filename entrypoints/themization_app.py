"""start script for mass themization"""
import sys
sys.path.insert(0, '..')
from mprorp.analyzer.theming.themer import mass_themization
from mprorp.analyzer.theming.test import get_estimate

if __name__ == '__main__':
    print("STARTING MASS THEMIZATION")
    mass_themization()
    get_estimate()
    print("MASS THEMIZATION COMPLETE")
