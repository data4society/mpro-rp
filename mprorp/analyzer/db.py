from mprorp.db.dbDriver import *
import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from datetime import datetime
from sqlalchemy import desc
import numpy as np

session = Driver.DBSession()


# reading document plain text from db
def get_doc(doc_id):
    return select(Document.stripped, Document.doc_id == doc_id).fetchone()[0]


# writing result of morphological analysis of document in db
def put_morpho(doc_id, morpho, new_status):
    new_document = Document(doc_id=doc_id, morpho=morpho)
    if new_status > 0:
        new_document.status = new_status
    update(new_document)


# reading result of morphological analysis of document from db
def get_morpho(doc_id):
    return select(Document.morpho, Document.doc_id == doc_id).fetchone()[0]


# writing lemmas frequently of document in db
def put_lemmas(doc_id, lemmas, new_status):
    some_doc = session.query(Document).filter(Document.doc_id == doc_id).one()
    some_doc.lemmas = lemmas
    if new_status > 0:
        some_doc.status = new_status
    session.commit()


# reading lemmas frequently of document from db
def get_lemmas(doc_id):
    return session.query(Document.lemmas).filter(Document.doc_id == doc_id).one().lemmas


# reading lemmas frequently of all documents in training set from db
def get_lemmas_freq(set_id):
    training_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    few_things = session.query(Document.doc_id, Document.lemmas).filter(
        Document.doc_id.in_(training_set.doc_ids)).all()
    result = {}
    for one_thing in few_things:
        result[str(one_thing[0])] = one_thing[1]
    return result
    # return {'id1': {'тип': 1, 'становиться': 3}, 'id2': {'тип': 1, 'есть': 2}}


# compression big disperse vector in 2 small vectors
def compress(array):
    indexes = []
    result = []
    size = len(array)
    for i in range(size):
        if array[i] != 0:
            indexes.append(i)
            result.append(array[i])
    return result, indexes


# uncompression from 2 small vectors in big disperse vector with 'size' elements
def uncompress(array, indexes, size):
    result = np.zeros(size, dtype=float)
    size_small = len(indexes)
    for i in range(size_small):
        result[indexes[i]] = array[i]
    return result


# writing training set parameters (idf, object-features matrix and indexes of lemmas and documents in it) db
def put_training_set_params(set_id, idf,  doc_index, lemma_index, object_features):
    some_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    some_set.idf = idf
    some_set.doc_index = doc_index
    some_set.lemma_index = lemma_index
    for doc_id in doc_index:
        features, indexes = compress(object_features[doc_index[doc_id], :])
        session.query(ObjectFeatures).filter(
            (ObjectFeatures.doc_id == doc_id) & (ObjectFeatures.set_id == set_id)).delete()
        session.add(ObjectFeatures(doc_id=doc_id, set_id=set_id, compressed=True, features=features, indexes=indexes))
    session.commit()


# writing new training set in db
def put_training_set(doc_id_array):
    new_set = TrainingSet()
    new_set.doc_ids = doc_id_array
    session.add(new_set)
    session.commit()
    return new_set.set_id


# reading answers for one rubric and all documents in set
def get_answers(set_id, rubric_id):
    docs = Driver.select(TrainingSet.doc_ids, TrainingSet.set_id == set_id).fetchone()[0]
    # docs = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    docs_rubric = session.query(DocumentRubric.doc_id).filter(
        (DocumentRubric.rubric_id == rubric_id) & (DocumentRubric.doc_id.in_(docs))).all()

    result = {}
    for doc_id in docs:
        result[str(doc_id)] = 0
    for doc_id in docs_rubric:
        result[str(doc_id[0])] = 1
    return result


# reading answer for one document and one rubric
def get_answer_doc(doc_id, rubric_id):
    doc_rubric = session.query(DocumentRubric.doc_id).filter(
        (DocumentRubric.rubric_id == rubric_id) & (DocumentRubric.doc_id == doc_id)).all()
    return len(doc_rubric)


# reading object-features matrix and index of documents in it
def get_doc_index_object_features(set_id):
    my_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    doc_index = my_set.doc_index
    lemma_num = len(my_set.lemma_index)
    result = session.query(ObjectFeatures).filter(ObjectFeatures.set_id == set_id).all()
    docs_num = len(doc_index)
    object_features = np.zeros((docs_num, lemma_num))
    for row in result:
        if row.compressed:
            object_features[doc_index[str(row.doc_id)], :] = uncompress(row.features, row.indexes, lemma_num)
        else:
            object_features[doc_index[str(row.doc_id)], :] = row.features
    return doc_index, object_features


# reading documents in set
def get_set_docs(set_id):
    return select(TrainingSet.doc_ids, TrainingSet.set_id == set_id).fetchone()[0]



# writing model compute for one rubric (rubric_id) with training set (set_id) using selected features (features)
def put_model(rubric_id, set_id, model, features, features_number):
    new_model = RubricationModel()
    new_model.rubric_id = rubric_id
    new_model.set_id = set_id
    new_model.model = model
    new_model.features = features
    new_model.features_num = features_number
    new_model.learning_date = datetime.now()
    insert(new_model)


# reading set_id of last computing model for rubric_id
def get_set_id_by_rubric_id(rubric_id):
    # ...
    res = session.query(RubricationModel.set_id, RubricationModel.learning_date).filter(
        RubricationModel.rubric_id == rubric_id).order_by(desc(RubricationModel.learning_date)).all()[0]
    # print(res.learning_date)
    return str(res.set_id)


# reading last computing model for rubric_id and set_id
def get_model(rubric_id, set_id):
    model = session.query(RubricationModel.model,
                          RubricationModel.features,
                          RubricationModel.features_num,
                          RubricationModel.model_id,
                          RubricationModel.learning_date).filter(
                          (RubricationModel.rubric_id == rubric_id) &
                          (RubricationModel.set_id == set_id)).order_by(
                          desc(RubricationModel.learning_date)).all()[0]
    # print(model[4])
    return {'model': model[0], 'features': model[1], 'features_num': model[2], 'model_id': str(model[3])}


# get dict with idf and lemma_index for each set_id
# sets[...] is dict: {'idf':..., 'lemma_index': ...}
def get_idf_lemma_index_by_set_id(sets_id):
    few_things = session.query(TrainingSet.set_id, TrainingSet.idf, TrainingSet.lemma_index).filter(
        TrainingSet.set_id.in_(sets_id)).all()
    result = {}
    for one_thing in few_things:
        result[str(one_thing[0])] = {'idf': one_thing[1], 'lemma_index': one_thing[2]}
    return result

# get lemma_index for one set_id
def get_lemma_index(set_id):
    return session.query(TrainingSet.lemma_index).filter(TrainingSet.set_id == set_id).one()[0]


# writing result of rubrication for one document
def put_rubrics(doc_id, rubrics, new_status):
    for rubric_id in rubrics:
        session.query(RubricationResult).filter(
            (RubricationResult.doc_id == doc_id) & (RubricationResult.rubric_id == rubric_id) &
            (RubricationResult.model_id == rubrics[rubric_id]['model_id'])).delete()
        session.add(RubricationResult(doc_id=doc_id, rubric_id=rubric_id, model_id=rubrics[rubric_id]['model_id'],
                                      result=rubrics[rubric_id]['result']))
    if new_status > 0:
        doc = session.query(Document).filter(Document.doc_id == doc_id).one()
        doc.rubric_ids = [k for k in rubrics if rubrics[k].result]
        doc.status = new_status
    session.commit()


# reading result of rubrication for model, training set and rubric
def get_rubrication_result(model_id, set_id, rubric_id):
    docs = Driver.select(TrainingSet.doc_ids, TrainingSet.set_id == set_id).fetchone()[0]
    rubrication_result = session.query(RubricationResult.doc_id, RubricationResult.result).filter(
        (RubricationResult.model_id == model_id) &
        (RubricationResult.rubric_id == rubric_id) &
        (RubricationResult.doc_id.in_(docs))).all()
    result = {}
    for doc_id in rubrication_result:
        result[str(doc_id[0])] = doc_id[1]
    return result
