"""program configuration"""
# base settings config
maindb_connection = ''
testdb_connection = 'postgres://postgres:@localhost:5432/mprorp'  # for travis db
try:
    # trying override base settings with custom
    from mprorp.config.local_settings import *
except ImportError:
    pass
