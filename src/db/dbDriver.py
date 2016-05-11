from sqlalchemy import create_engine
from config.settings import *


class dbDriver:

    database = create_engine(DATABASE_ENGINE+'://'+DATABASE_USER+':'+DATABASE_PASSWORD+'@'+DATABASE_HOST+'/'+DATABASE_NAME)
    '''
    @staticmethod
    def connect():
        e
        pass;
    '''
