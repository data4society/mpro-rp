"""other app as crawler source"""
from mprorp.crawler.utils import *
from mprorp.db.models import *

from sqlalchemy.orm import load_only


def other_app_cloning(other_app_id, blacklist, url_domain, fields_to_clone, complete_status, app_id, session):
    """download google news start feed and feeds for every story"""
    # download google news start feed
    origin_docs = session.query(Document).filter_by(app_id=other_app_id, status=complete_status).all()
    docs = []
    for origin_doc in origin_docs:
        url = origin_doc.url
        origin_doc_id = str(origin_doc.doc_id)
        if check_url_with_blacklist(url, blacklist):
            print("BLACKLIST STOP: " + url)
            break
        new_doc = Document(app_id=app_id)
        for field in fields_to_clone:
            setattr(new_doc, field, getattr(origin_doc, field))
        new_doc.guid = app_id+url
        record_id = str(session.query(Record).filter_by(source=origin_doc_id).options(load_only("document_id")).first().document_id)
        new_doc.url = url_domain+'/#page=inbox,documentId='+record_id+',app='+other_app_id
        meta = origin_doc.meta
        meta["source_record_id"] = origin_doc_id
        new_doc.meta = meta
        session.add(new_doc)
        docs.append(new_doc)
    return docs


if __name__ == '__main__':
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    other_app_cloning('https://www.google.ru/alerts/feeds/01670104253645512148/17155994496834907056') #f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))