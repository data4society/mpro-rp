"""yandex news mail parser"""

from mprorp.db.models import *
import csv
from mprorp.utils import relative_file_path
import datetime

def csv_start_parsing(source, app_id, session):
    """download google news start feed and feeds for every story"""

    docs = []
    with open(relative_file_path(__file__, '../data/csv_to_rubrication/'+source+'.csv'), 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            rubric = session.query(Rubric).filter_by(name=row[0]).first()
            url = row[1]
            date = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())
            if session.query(Document).filter_by(guid=app_id + url).count() == 0:
                meta = dict()
                meta["publisher"] = dict()
                doc = Document(guid=app_id + url, app_id=app_id, url=url, status=0, type='article', meta=meta, rubric_ids=[rubric.rubric_id], published_date=date)
                session.add(doc)
                docs.append(doc)
            else:
                doc = session.query(Document).filter_by(guid=app_id + url).first()
                rubric_ids = list(doc.rubric_ids)
                rubric_ids.append(rubric.rubric_id)
                doc.rubric_ids = rubric_ids
            #doc_rubric = DocumentRubric(doc=doc, rubric=rubric)
            #session.add(doc_rubric)
    return docs


if __name__ == '__main__':
    from mprorp.db.dbDriver import *
    session = db_session()
    csv_start_parsing('mpro-urls_to_csv', 'test', session)
    session.commit()
    session.remove()