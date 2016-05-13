from config.settings import *

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine




class dbDriver:
    engine = create_engine(DATABASE_ENGINE+'://'+DATABASE_USER+':'+DATABASE_PASSWORD+'@'+DATABASE_HOST+'/'+DATABASE_NAME)

    DBSession = sessionmaker(bind=engine)
    '''
    @staticmethod
    def connect():
        e
        pass;
    '''

Base = declarative_base()
import db.models
Base.metadata.create_all(dbDriver.engine)
Base.metadata.bind = dbDriver.engine
