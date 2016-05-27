"""database driver for more simple working with sqlalchemy and postgres"""
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy
import sys


from mprorp.config.settings import *

if "maindb" in sys.argv:
    connection_string = maindb_connection
else:
    connection_string = testdb_connection
engine = create_engine(connection_string)
meta = MetaData(bind=engine, reflect=True)
DBSession = sessionmaker(bind=engine)
Base = declarative_base()

if "maindb" in sys.argv:
    import mprorp.db.models

    Base.metadata.create_all(engine)


def insert(new_object):
    session = DBSession()
    session.add(new_object)
    session.commit()
    return


def select(columns, where_clause):
    if type(columns) is list:
        return engine.execute(sqlalchemy.select(columns).where(where_clause))
    else:
        return engine.execute(sqlalchemy.select([columns]).where(where_clause))


def update(obj):
    session = DBSession()
    session.merge(obj)
    session.commit()
    return obj;
    #obj = meta.tables[table_name]
    #return engine.execute(sqlalchemy.update().where(where_clause).values(values))
    #return DBDriver.engine.execute(obj.update().values(values).where(where_clause))#obj.c.doc_id == '7a074073-7747-47b9-aba0-1f5990ddbaf9'))



def dropall_and_create():
    DBSession.close_all()
    for tbl in reversed(meta.sorted_tables):
        tbl.drop(engine);
    import mprorp.db.models
    Base.metadata.create_all(engine)
