"""start script for mass themization"""
import sys
sys.path.insert(0, '..')
from mprorp.db.dbDriver import delete_app_documents, delete_document

if __name__ == '__main__':
    print("START DELETING")
    delete_document('f83eaba6-be71-4472-81f0-f57b8838461b')
    print("DELETING COMPLETE")
