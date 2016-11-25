"""yandex news mail parser"""

from mprorp.db.models import *
import csv
from mprorp.utils import relative_file_path


def csv_start_parsing(source, app_id, session):
    """download google news start feed and feeds for every story"""

    docs = []
    with open(relative_file_path(__file__, '../data/csv_to_rubrication/'+source+'.csv'), 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            rubric = session.query(Rubric).filter_by(name=row[0]).first()
            url = row[1]
            new_doc = Document(guid=app_id + url, url=url, status=0, type='article', rubric_ids=[rubric.rubric_id])
            doc_rubric = DocumentRubric(doc=new_doc, rubric=rubric)
            session.add(new_doc)
            session.add(doc_rubric)
            docs.append(new_doc)
    return docs


if __name__ == '__main__':
    from mprorp.db.dbDriver import *
    session = db_session()
    csv_start_parsing('mpro-urls_to_csv', 'test', session)
    #session.commit()
    #session.remove()