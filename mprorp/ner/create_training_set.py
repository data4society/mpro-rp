import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb

def create_training_set(rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    new_docs = session.query(Document).filter_by(status=1200).all()
    ids = []
    for doc in new_docs:
     if rubric_id in str(doc.rubric_ids):
      ids.append(doc.doc_id)
    b = (len(ids) // 5) * 4
    tr_set = ids[:b]
    test_set = ids[b:]
    free_docs = session.query(Document).filter_by(rubric_ids=None, status=1200)[:b]
    for doc in free_docs:
     tr_set.append(doc.doc_id)
    free_docs = session.query(Document).filter_by(rubric_ids=None, status=1200)[b:b+len(test_set)]
    for doc in free_docs:
        test_set.append(doc.doc_id)
    return [tr_set, test_set]



def add_rubric_to_doc(new_doc_ids, rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    old_ids = session.query(DocumentRubric.doc_id).all()
    for new_doc_id in new_doc_ids:
        if new_doc_id not in old_ids:
            rubric_id_new = session.query(Document.rubric_ids).filter_by(doc_id=new_doc_id)[0][0]
            print(rubric_id_new)
            if rubric_id_new is not None:
                new_id = DocumentRubric(doc_id = new_doc_id, rubric_id = rubric_id)
                session.add(new_id)
    session.commit()


def write_training_set(rubric_id, session=None):
 training_set = create_training_set(rubric_id)[0]
 if session is None:
  session = Driver.db_session()
 new_set = TrainingSet(doc_ids=training_set, doc_num=len(training_set), name='Matvey_set')
 session.add(new_set)
 session.commit()


def teach_rubricator(set_id, rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    docs = session.query(TrainingSet.doc_ids).filter_by(set_id=set_id)[0][0]
    n = len(docs)
    for doc_id in docs:
        print(str(n) + ' docs left')
        rb.morpho_doc2(str(doc_id))
        rb.lemmas_freq_doc2(str(doc_id))
        n -= 1
    rb.idf_object_features_set(set_id)
    rb.learning_rubric_model(set_id, rubric_id)

def test_model(set_id, rubric_id):
    for doc_id in create_training_set(rubric_id[1]):
        rb.spot_doc_rubrics2(doc_id, {rubric_id: None})

    model_id = db.get_model(rubric_id, set_id)["model_id"]

    result = rb.f1_score(model_id, set_id, rubric_id)
    return result


#1 Создание обучающей выборки
print(len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[0]), len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[1])) #свобода ассоциаций
print(len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[0]), len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[1])) #свобода собраний
#2 Запись в таблицу DocumentRubrics
add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[0], '19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций
add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[0], '19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний
add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[1], '19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций
add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[1], '19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний
#3 Запись в таблицу TrainingSet
write_training_set('19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций
write_training_set('19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний
#4 Обучение
#teach_rubricator(training_set_id, '19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций
#teach_rubricator(training_set_id, '19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний
#5 Тест
#print(test_model(training_set_id, '19848dd0-436a-11e6-beb8-9e71128cae21')) #свобода ассоциаций
#print(test_model(training_set_id, '19848dd0-436a-11e6-beb8-9e71128cae02')) #свобода собраний

