import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from mprorp.analyzer.db import put_training_set

def create_training_set(rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    new_docs = session.query(Document).filter_by(status=1200)
    ids = []
    for doc in new_docs:
     if rubric_id in str(doc.rubric_ids):
      ids.append(doc.doc_id)
    tr_set = ids[:100]
    free_docs = session.query(Document).filter_by(rubric_ids=None)[:100]
    for doc in free_docs:
     tr_set.append(doc.doc_id)
    return tr_set


def add_rubric_to_doc(rubrics_dic, rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    for document_id in rubrics_dic[rubric_id]:
        new_id = DocumentRubric(doc_id = str(document_id), rubric_id = str(rubric_id))
        session.add(new_id)
    session.commit()

#add_rubric_to_doc(rubrics, '19848dd0-436a-11e6-beb8-9e71128cae02')
#add_rubric_to_doc(rubrics, '19848dd0-436a-11e6-beb8-9e71128cae21')

def write_training_set(rubric_id, session=None):
 training_set = []
 for doc_id in create_training_set(rubric_id):
  training_set.append(str(doc_id))
 if session is None:
  session = Driver.db_session()
 new_set = TrainingSet(doc_ids=set(training_set), doc_num=len(training_set))
 session.add(new_set)
 session.commit()

#write_training_set('19848dd0-436a-11e6-beb8-9e71128cae02') не работает

#put_training_set(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')) так тоже