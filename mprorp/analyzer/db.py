from mprorp.db.dbDriver import *
import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from datetime import datetime
from sqlalchemy import desc

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
    docs = Driver.select(TrainingSet.doc_refs,TrainingSet.set_id == set_id).fetchone()[0]
    #docs_rubric = Driver.select(DocumentRubric.doc_id, (DocumentRubric.doc_id in (docs)) and (DocumentRubric.rubric_id == rubric_id)).fetchall()
    #docs_rubric = Driver.select(DocumentRubric.doc_id, (DocumentRubric.doc_id in (docs))).fetchall()

    #docs = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    docs_rubric = session.query(DocumentRubric.doc_id).filter((DocumentRubric.rubric_id == rubric_id) & (DocumentRubric.doc_id.in_(docs))).all()

    result = {}
    for doc_id in docs:
        result[str(doc_id)] = 0
    for doc_id in docs_rubric:
        result[str(doc_id[0])] = 1
    return result

def get_answer_doc(doc_id, rubric_id):

    doc_rubric = session.query(DocumentRubric.doc_id).filter((DocumentRubric.rubric_id == rubric_id) & (DocumentRubric.doc_id == doc_id)).all()
    return len(doc_rubric)

def get_doc_index_object_features(set_id):
    result = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    #result = select(TrainingSet, TrainingSet.set_id == set_id).fetchone()[0]
    #rint(result)
    return result.doc_index, result.object_features

def get_set_docs(set_id):
    return select(TrainingSet.doc_refs,TrainingSet.set_id == set_id).fetchone()[0]

def put_model(rubric_id, set_id, model, features, features_number):
    new_model = RubricationModel()
    new_model.rubric_id = rubric_id
    new_model.set_id    = set_id
    new_model.model     = model
    new_model.features  = features
    new_model.features_num  = features_number
    new_model.learning_date = datetime.now()
    insert(new_model)

def get_set_id_by_rubric_id(rubric_id):
    #...
    res = session.query(RubricationModel.set_id, RubricationModel.learning_date).filter(RubricationModel.rubric_id == rubric_id).order_by(desc(RubricationModel.learning_date)).all()[0]
    # print(res.learning_date)
    return str(res.set_id)

def get_model(rubric_id, set_id):
    model = session.query(RubricationModel.model, RubricationModel.features, RubricationModel.features_num, RubricationModel.model_id, RubricationModel.learning_date).filter(
        (RubricationModel.rubric_id == rubric_id) & (RubricationModel.set_id == set_id)).order_by(desc(RubricationModel.learning_date)).all()[0]
    # print(model[4])
    return {'model': model[0], 'features': model[1], 'features_num': model[2], 'model_id': str(model[3])}

# get dict with idf and lemma_index for each set_id
# sets[...] is dict: {'idf':..., 'lemma_index': ...}
def get_idf_lemma_index_by_set_id(sets_id):
    few_things = session.query(TrainingSet.set_id, TrainingSet.idf, TrainingSet.lemma_index).filter(TrainingSet.set_id.in_(sets_id)).all()
    result = {}
    for one_thing in few_things:
        result[str(one_thing[0])] = {'idf': one_thing[1], 'lemma_index': one_thing[2]}
    return result

def put_rubrics(doc_id, rubrics):
    for rubric_id in rubrics:
        new_result = RubricationResult()
        new_result.doc_id = doc_id
        new_result.rubric_id = rubric_id
        new_result.model_id = rubrics[rubric_id]['model_id']
        new_result.result = rubrics[rubric_id]['result']
