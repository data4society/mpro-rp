"""bad documents as crawler source"""
from mprorp.crawler.utils import *
from mprorp.db.models import *

from sqlalchemy.orm import load_only


def refactor_start_parsing(start_status, new_status, from_date, app_id, session):
    """get all docs by condition and set status"""
    docs = session.query(Document).filter_by(app_id=app_id, status=start_status).filter(Document.created >= from_date).all()
    docs = []
    for doc in docs:
        doc.status = new_status
    return docs


if __name__ == '__main__':
    pass