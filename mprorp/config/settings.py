"""program configuration"""
# The database settings are left blank so to force the use of local_settings.py below
maindb_connection = ''
testdb_connection = 'postgres://postgres:@localhost:5432/mprorp' # travis db
try:
    from mprorp.config.local_settings import *
except ImportError:
    pass;