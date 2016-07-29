import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
import mprorp.analyzer.db as db
from mprorp.analyzer.db import put_training_set
import mprorp.analyzer.rubricator as rb

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
  training_set.append(doc_id)
 if session is None:
  session = Driver.db_session()
 new_set = TrainingSet(doc_ids=training_set, doc_num=len(training_set))
 session.add(new_set)
 session.commit()

#write_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')
#print('Done')
#write_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')
#print('Done')
#put_training_set(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')) так тоже

def test_rubricator(set_id, rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    docs = session.query(TrainingSet.doc_ids).filter_by(set_id=set_id)
    for doc_id in docs:
        rb.morpho_doc2(str(doc_id))
        rb.lemmas_freq_doc2(str(doc_id))
    rb.idf_object_features_set(set_id)
    rb.learning_rubric_model(set_id, rubric_id)

    for doc_id in db.get_set_docs(set_id):
        rb.spot_doc_rubrics2(doc_id, {rubric_id: None})
        # check we can overwrite rubrication results:
        rb.spot_doc_rubrics2(doc_id, {rubric_id: None})

    model_id = db.get_model(rubric_id, set_id)["model_id"]

    result = rb.f1_score(model_id, set_id, rubric_id)
    return result

print(test_rubricator('7784ced1-7520-4e16-99f6-c6fd656311b9','19848dd0-436a-11e6-beb8-9e71128cae21'))


#session = Driver.db_session()
#a = session.query(TrainingSet.doc_ids).filter_by(set_id='9460c953-a5f8-4c55-97cc-f1ed3905c89f')
#b = session.query(TrainingSet.doc_ids).filter_by(set_id='0cbf3533-cb40-43f0-96bb-943152a877e1')

#for i in a:
#    print(i)
#for i in b:
#    print(b)