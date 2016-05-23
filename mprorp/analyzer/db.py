from mprorp.db.dbDriver import *
import mprorp.db.dbDriver as Driver
from mprorp.db.models import *

session = Driver.DBSession()

def get_doc(doc_id):
    return select(Document.stripped, Document.doc_id == doc_id).fetchone()[0]

def put_morpho(doc_id, morpho):
    update(Document(doc_id = doc_id, morpho = morpho))
    #some_doc = session.query(Document).filter(Document.doc_id == doc_id).one()
    #some_doc.morpho = morpho
    #session.commit()

def get_morpho(doc_id):
    return select(Document.morpho, Document.doc_id == doc_id).fetchone()[0]

def put_lemmas(doc_id,lemmas):
    some_doc = session.query(Document).filter(Document.doc_id == doc_id).one()
    some_doc.lemmas = lemmas
    session.commit()

def get_lemmas(doc_id):
    return session.query(Document.lemmas).filter(Document.doc_id == doc_id).one().lemmas

def get_lemmas_freq ( set_id ):
    training_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    few_things = session.query(Document.doc_id, Document.lemmas).filter(Document.doc_id.in_(training_set.doc_refs)).all()
    result = {}
    for one_thing in few_things:
        result[str(one_thing[0])] = one_thing[1]
    return result
    #return {'id1': {'тип': 1, 'становиться': 3}, 'id2': {'тип': 1, 'есть': 2}}

def put_training_set_params(set_id, idf,  doc_index, lemma_index, object_features):
    some_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    some_set.idf = idf
    some_set.doc_index = doc_index
    some_set.lemma_index = lemma_index
    some_set.object_features = object_features
    session.commit()

def put_training_set(doc_id_array):
    new_set = TrainingSet()
    new_set.doc_ref = doc_id_array
    session.add(new_set)
    session.commit()
    return new_set.set_id

def get_answers(set_id, rubric_id):
    #docs = Driver.select(TrainingSet.doc_refs,TrainingSet.set_id == set_id).fetchone()[0]
    #docs_rubric = Driver.select(DocumentRubric.doc_id, (DocumentRubric.doc_id in (docs)) and (DocumentRubric.rubric_id == rubric_id)).fetchall()
    #docs_rubric = Driver.select(DocumentRubric.doc_id, (DocumentRubric.doc_id in (docs))).fetchall()

    docs = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    docs_rubric = session.query(DocumentRubric.doc_id).filter((DocumentRubric.rubric_id == rubric_id) and (DocumentRubric.doc_id.in_(docs.doc_refs))).all()


    print(docs_rubric)
    #result = dict.fromkeys( docs, value=0)
    result = {}
    for doc_id in docs.doc_refs:
        result[str(doc_id)] = 0
    for doc_id in docs_rubric:
        result[str(doc_id)] = 1
    return result

def get_doc_index_object_features(set_id):
    result = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    #result = select(TrainingSet, TrainingSet.set_id == set_id).fetchone()[0]
    #rint(result)
    return result.doc_index, result.object_features

def get_set_docs(set_id):
    return select(TrainingSet.doc_refs,TrainingSet.set_id == set_id).fetchone()[0]
