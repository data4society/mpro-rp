"""program configuration"""
# base settings config
maindb_connection = ''
testdb_connection = 'postgres://postgres:@localhost:5432/mprorp'  # for travis db
google_private_key_id = ''
google_private_key = ''
google_client_email = ''
google_client_id = ''
google_spreadsheet_id = ''

tomita_log_path = ''

try:
    # trying override base settings with custom
    from mprorp.config.local_settings import *
except ImportError:
    pass
