from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from mprorp.config.settings import *


class DBDriver:
    engine = create_engine(DATABASE_ENGINE+'://'+DATABASE_USER+':'+DATABASE_PASSWORD+'@'+DATABASE_HOST+'/'+DATABASE_NAME)
    print(DATABASE_ENGINE+'://'+DATABASE_USER+':'+DATABASE_PASSWORD+'@'+DATABASE_HOST+'/'+DATABASE_NAME)
    meta = MetaData(bind=engine, reflect=True)
    DBSession = sessionmaker(bind=engine)

    @staticmethod
    def insert(new_object):
        session = DBDriver.DBSession()
        session.add(new_object)
        session.commit()
        return

    @staticmethod
    def select_equal(table_name, needed_column, where_column, where_value):
        obj = DBDriver.meta.tables[table_name]
        return \
        DBDriver.engine.execute(select([obj.c[needed_column]]).where(obj.c[where_column] == where_value)).fetchone()[0]

    @staticmethod
    def select(columns, where_clause):
        return DBDriver.engine.execute(select([columns]).where(where_clause))

    @staticmethod
    def update(table_name, where_clause, **values):
        obj = DBDriver.meta.tables[table_name]
        return DBDriver.engine.execute(update().where(where_clause).values(values))
        #return DBDriver.engine.execute(obj.update().values(values).where(where_clause))#obj.c.doc_id == '7a074073-7747-47b9-aba0-1f5990ddbaf9'))

Base = declarative_base()
import mprorp.db.models
Base.metadata.create_all(DBDriver.engine)
Base.metadata.bind = DBDriver.engine
