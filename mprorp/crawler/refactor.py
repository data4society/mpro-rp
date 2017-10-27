"""bad documents as crawler source"""
from mprorp.crawler.utils import *
from mprorp.db.models import *

from sqlalchemy.orm import load_only


def refactor_start_parsing(start_status, new_status, from_date, app_id, session):
    """get all docs by condition and set status"""
    docs = session.query(Document.doc_id).filter_by(app_id=app_id, status=start_status).filter(Document.created >= from_date).all()
    doc_ids = [doc[0] for doc in docs]
    if doc_ids and start_status != new_status:
        session.query(Document).filter_by(app_id=app_id, status=start_status).filter(Document.created >= from_date).update({"status": new_status})
        session.commit()
    return doc_ids


if __name__ == '__main__':
    pass