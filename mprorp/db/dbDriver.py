"""database driver for more simple working with sqlalchemy and postgres"""

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.pool import NullPool
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import load_only
import sqlalchemy
import sys
from multiprocessing.util import register_after_fork
from mprorp.config.settings import *
from os import getcwd

if ("maindb" in sys.argv) or ("worker" in sys.argv) or (getcwd().split("/")[-1] == "entrypoints"):
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


def variable_set(name, value, session=None):
    from mprorp.db.models import Variable
    has_session = True
    if not session:
        has_session = False
        session = db_session()
    var = session.query(Variable).filter(Variable.name == name).first()
    if not var:
        var = Variable(name=name, json=dict())
        session.add(var)
    var.json["value"] = value
    flag_modified(var, "json")

    if not has_session:
        session.commit()
        session.remove()


def variable_get(name, value=0, session=None):
    has_session = True
    if not session:
        has_session = False
        session = db_session()
    from mprorp.db.models import Variable
    var = session.query(Variable).filter(Variable.name == name).first()
    if var:
        val = var.json["value"]
    else:
        val = value
        variable_set(name, value, session)
    if not has_session:
        session.commit()
        session.remove()
    return val


def dropall_and_create():
    """drop all tables and create all them again"""
    # close sessions
    if db_type == "server":
        print("What's the fuck??? You are trying to drop working database!!!")
        exit()
    DBSession = sessionmaker(bind=engine)
    DBSession.close_all()
    #drop all which exist
    for tbl in reversed(meta.sorted_tables):
        try:
            tbl.drop(engine)
        except Exception:
            pass;
    # load models
    import mprorp.db.models
    # create tables by models
    Base.metadata.create_all(engine)


def delete_document(doc_id, session=None, force_commit=False, full=True):
    has_session = True
    if not session:
        has_session = False
        session = db_session()
    session.execute("DELETE FROM mentions USING markups m WHERE m.markup_id = markup AND m.document = '" + doc_id + "'")
    session.execute(
        "DELETE FROM public.\"references\" USING markups m WHERE m.markup_id = markup AND m.document = '" + doc_id + "'")
    session.execute("DELETE FROM markups m WHERE m.document = '" + doc_id + "'")
    session.execute("DELETE FROM rubricationresults r WHERE r.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM documentrubrics d WHERE d.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM tomita_results d WHERE d.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM objectfeatures o WHERE o.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM ner_features n WHERE n.doc_id = '" + doc_id + "'")
    session.execute(
        "DELETE FROM changes c USING records r WHERE c.document_id = r.document_id AND r.source = '" + doc_id + "'")
    session.execute("DELETE FROM records WHERE source = '" + doc_id + "'")
    if full:
        session.execute("DELETE FROM documents WHERE doc_id = '" + doc_id + "'")
    else:
        session.execute("UPDATE documents SET doc_source=NULL, stripped=NULL, morpho=NULL, lemmas=NULL, title=NULL, meta=NULL, publisher_id=NULL, published_date=NULL, source_with_type=NULL WHERE doc_id = '" + doc_id + "'")
    if not has_session:
        session.commit()
        session.remove()
    elif force_commit:
        session.commit()
    print(doc_id, "complete deletion")


def cleaning_document(doc, session=None, force_commit=False):
    doc_id = str(doc.doc_id)
    has_session = True
    if not session:
        has_session = False
        session = db_session()
    session.execute("DELETE FROM mentions USING markups m WHERE m.markup_id = markup AND m.document = '" + doc_id + "'")
    session.execute(
        "DELETE FROM public.\"references\" USING markups m WHERE m.markup_id = markup AND m.document = '" + doc_id + "'")
    session.execute("DELETE FROM markups m WHERE m.document = '" + doc_id + "'")
    session.execute("DELETE FROM rubricationresults r WHERE r.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM documentrubrics d WHERE d.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM tomita_results d WHERE d.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM objectfeatures o WHERE o.doc_id = '" + doc_id + "'")
    session.execute("DELETE FROM ner_features n WHERE n.doc_id = '" + doc_id + "'")
    #session.execute("UPDATE documents SET morpho=DEFAULT WHERE doc_id = '" + doc_id + "'")
    doc.morpho = None
    if not has_session:
        session.commit()
        session.remove()
    elif force_commit:
        session.commit()


def delete_app_documents(app_id, status=-1):
    from mprorp.db.models import Document
    session = db_session()
    if status == -1:
        docs = session.query(Document).filter_by(app_id=app_id).options(load_only("doc_id")).all()
    else:
        docs = session.query(Document).filter_by(app_id=app_id, status=status).options(load_only("doc_id")).all()
    print("ATTENTION!!! DELETING FROM APP: "+app_id+" documents length:", len(docs))
    n = 0
    for doc in docs:
        delete_document(str(doc.doc_id), session, True)
        n += 1
        print(n)
    session.remove()