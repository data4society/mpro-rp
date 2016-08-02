"""database driver for more simple working with sqlalchemy and postgres"""

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.pool import NullPool
import sqlalchemy
import sys
from multiprocessing.util import register_after_fork
from mprorp.config.settings import *

if ("maindb" in sys.argv) or ("worker" in sys.argv) or ("ner_learning_app.py" in sys.argv):
    db_type = "server"
else:
    db_type = "local"

if db_type == "server":
    connection_string = maindb_connection
else:
    connection_string = testdb_connection

# main object which SQLA uses to connect to database
engine = create_engine(connection_string, convert_unicode=True, poolclass=NullPool)  # pool_recycle=3600, pool_size=10)
register_after_fork(engine, engine.dispose)
# full meta information about structure of tables
meta = MetaData(bind=engine, reflect=True)
# session class
#DBSession = sessionmaker(bind=engine)
#DBSession.close_all()
Base = declarative_base()

if db_type == "server":
    import mprorp.db.models
    # if any table doesn't exist it will create at this step
    Base.metadata.create_all(engine)

print("INIT DB")

def db_session():
    return scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

def insert(new_object):
    """insert to database with ORM"""
    session = db_session()
    session.add(new_object)
    session.commit()
    return


def select(columns, where_clause):
    """select with query api"""
    if type(columns) is list:
        return engine.execute(sqlalchemy.select(columns).where(where_clause))
    else:
        return engine.execute(sqlalchemy.select([columns]).where(where_clause))


def update(obj):
    """update with ORM"""
    session = db_session()
    session.merge(obj)
    session.commit()
    return obj;
    #o bj = meta.tables[table_name]
    # return engine.execute(sqlalchemy.update().where(where_clause).values(values))
    # return DBDriver.engine.execute(obj.update().values(values).where(where_clause))#obj.c.doc_id == '7a074073-7747-47b9-aba0-1f5990ddbaf9'))


def delete(table_name, where_clause):
    """delete with query api"""
    engine.execute(sqlalchemy.delete(meta.tables[table_name]).where(where_clause))


def dropall_and_create():
    """drop all tables and create all them again"""
    # close sessions
    DBSession = sessionmaker(bind=engine)
    DBSession.close_all()
    #drop all which exist
    for tbl in reversed(meta.sorted_tables):
        try:
            tbl.drop(engine);
        except Exception:
            pass;
    # load models
    import mprorp.db.models
    # create tables by models
    Base.metadata.create_all(engine)