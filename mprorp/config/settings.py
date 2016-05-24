# The database settings are left blank so to force the use of local_settings.py below
maindb_connection = ''
testdb_connection = 'aaaaa'
try:
    from mprorp.config.local_settings import *
except ImportError:
    pass;