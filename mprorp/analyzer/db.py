"""Functions for read/write in data base"""

from mprorp.db.dbDriver import *
import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from datetime import datetime
from sqlalchemy import desc
import numpy as np
import uuid


def doc_apply(doc_id, my_def, *args):
    """Apply functions my_def to doc_id and other arguments in *args """
    session = Driver.DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    result = my_def(doc, *args)
    session.commit()
    return  result


# writing result of morphological analysis of document in db
# def put_morpho(doc_id, morpho, new_status):
#     new_document = Document(doc_id=doc_id, morpho=morpho)
#     if new_status > 0:
#         new_document.status = new_status
#     update(new_document)


# reading result of morphological analysis of document from db
def get_morpho(doc_id, session=None):
    """reading result of morphological analysis of document from db"""
    if session is None:
        session = Driver.DBSession()
    return session.query(Document.morpho).filter(Document.doc_id == doc_id).one().morpho


# reading lemmas frequently of all documents in training set from db
def get_lemmas_freq(set_id, session=None):
    """reading lemmas frequently of all documents in training set from db"""
    if session is None:
        session = Driver.DBSession()
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
    """compression big disperse vector in 2 small vectors"""
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
    """uncompression from 2 small vectors in big disperse vector with 'size' elements"""
    result = np.zeros(size, dtype=float)
    size_small = len(indexes)
    for i in range(size_small):
        result[indexes[i]] = array[i]
    return result


# writing training set parameters (idf, object-features matrix and indexes of lemmas and documents in it) db
def put_training_set_params(set_id, idf,  doc_index, lemma_index, object_features, session=None, commit_session=True):
    """writing training set parameters (idf, object-features matrix and indexes of lemmas and documents in it) db"""
    if session is None:
        session = Driver.DBSession()
    some_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    some_set.idf = idf
    some_set.doc_index = doc_index
    some_set.lemma_index = lemma_index
    for doc_id in doc_index:
        features, indexes = compress(object_features[doc_index[doc_id], :])
        session.query(ObjectFeatures).filter(
            (ObjectFeatures.doc_id == doc_id) & (ObjectFeatures.set_id == set_id)).delete()
        session.add(ObjectFeatures(doc_id=doc_id, set_id=set_id, compressed=True, features=features, indexes=indexes))
    if commit_session:
        session.commit()


# writing new training set in db
def put_training_set(doc_id_array, session=None, commit_session=True):
    """writing new training set in db"""
    if session is None:
        session = Driver.DBSession()
    new_set = TrainingSet()
    new_set.doc_ids = doc_id_array
    session.add(new_set)
    if commit_session:
        session.commit()
    return new_set.set_id


# reading answers for one rubric and all documents in set
def get_rubric_answers(set_id, rubric_id, session=None):
    """reading answers for one rubric and all documents in set"""
    if session is None:
        session = Driver.DBSession()
    # docs = Driver.select(TrainingSet.doc_ids, TrainingSet.set_id == set_id).fetchone()[0]
    docs = session.query(TrainingSet.doc_ids).filter(TrainingSet.set_id == set_id).one().doc_ids
    docs_rubric = session.query(DocumentRubric.doc_id).filter(
        (DocumentRubric.rubric_id == rubric_id) & (DocumentRubric.doc_id.in_(docs))).all()

    result = {}
    for doc_id in docs:
        result[str(doc_id)] = 0
    for doc_id in docs_rubric:
        result[str(doc_id[0])] = 1
    return result


# reading object-features matrix and index of documents in it
def get_doc_index_object_features(set_id, session=None):
    """reading object-features matrix and index of documents in it"""
    if session is None:
        session = Driver.DBSession()
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
def get_set_docs(set_id, session=None):
    """reading documents in set"""
    if session is None:
        session = Driver.DBSession()
    return session.query(TrainingSet.doc_ids).filter(TrainingSet.set_id == set_id).one().doc_ids


# writing model compute for one rubric (rubric_id) with training set (set_id) using selected features (features)
def put_model(rubric_id, set_id, model, features, features_number, session=None, commit_session=True):
    if session is None:
        session = Driver.DBSession()
    new_model = RubricationModel()
    new_model.rubric_id = rubric_id
    new_model.set_id = set_id
    new_model.model = model
    new_model.features = features
    new_model.features_num = features_number
    new_model.learning_date = datetime.now()
    session.add(new_model)
    if commit_session:
        session.commit()


# reading set_id of last computing model for rubric_id
def get_set_id_by_rubric_id(rubric_id, session=None):
    """reading set_id of last computing model for rubric_id"""
    if session is None:
        session = Driver.DBSession()
    res = session.query(RubricationModel.set_id, RubricationModel.learning_date).filter(
        RubricationModel.rubric_id == rubric_id).order_by(desc(RubricationModel.learning_date)).all()[0]
    # print(res.learning_date)
    return str(res.set_id)


# reading last computing model for rubric_id and set_id
def get_model(rubric_id, set_id, session=None):
    """reading last computing model for rubric_id and set_id"""
    if session is None:
        session = Driver.DBSession()
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
def get_idf_lemma_index_by_set_id(sets_id, session=None):
    """get dict with idf and lemma_index for each set_id in sets_id.
    return {'set_id1':{'idf': ..., 'lemma_index':...},'set_id_2':...}"""
    if session is None:
        session = Driver.DBSession()
    few_things = session.query(TrainingSet.set_id, TrainingSet.idf, TrainingSet.lemma_index).filter(
        TrainingSet.set_id.in_(sets_id)).all()
    result = {}
    for one_thing in few_things:
        result[str(one_thing[0])] = {'idf': one_thing[1], 'lemma_index': one_thing[2]}
    return result


# get lemma_index for one set_id
def get_lemma_index(set_id, session=None):
    """get lemma_index for one set_id"""
    if session is None:
        session = Driver.DBSession()
    return session.query(TrainingSet.lemma_index).filter(TrainingSet.set_id == set_id).one()[0]


# writing result of rubrication for one document
def put_rubrics(answers, session=None, commit_session=True):
    """writing result of rubrication for one document"""
    if session is None:
        session = Driver.DBSession()
    for ans in answers:
        session.query(RubricationResult).filter(
            (RubricationResult.doc_id == ans['doc_id']) & (RubricationResult.rubric_id == ans['rubric_id']) &
            (RubricationResult.model_id == ans['model_id'])).delete()
        session.add(RubricationResult(doc_id=ans['doc_id'], rubric_id=ans['rubric_id'], model_id=ans['model_id'],
                                      result=ans['result'], probability=ans['probability']))
    if commit_session:
        session.commit()


# reading result of rubrication (probability) for model, training set and rubric
def get_rubrication_probability(model_id, set_id, rubric_id):
    """reading result of rubrication (probability) for model, training set and rubric"""
    return get_rubrication_result_probability(model_id, set_id, rubric_id, 2)


# reading result of rubrication (answers) for model, training set and rubric
def get_rubrication_result(model_id, set_id, rubric_id):
    """reading result of rubrication (answers) for model, training set and rubric"""
    return get_rubrication_result_probability(model_id, set_id, rubric_id, 1)


def get_rubrication_result_from_doc(set_id, rubric_id, session=None):
    """reading result of rubrication (answers) for set and rubric from documents"""
    if session is None:
        session = Driver.DBSession()
    # docs = Driver.select(TrainingSet.doc_ids, TrainingSet.set_id == set_id).fetchone()[0]
    docs = session.query(TrainingSet.doc_ids).filter(TrainingSet.set_id == set_id).one().doc_ids
    res = session.query(Document.doc_id, Document.rubric_ids).filter(
        (Document.doc_id.in_(docs))).all()
    result = {}
    for doc_id in docs:
        result[str(doc_id)] = 0
    for doc in res:
        for r_id in doc[1]:
            if rubric_id == str(r_id):
                result[str(doc[0])] = 1
                break
    return result


# reading result of rubrication (result_type - 1 or 2) for model, training set and rubric
def get_rubrication_result_probability(model_id, set_id, rubric_id, result_type, session=None):
    """reading result of rubrication (result_type - 1 or 2) for model, training set and rubric"""
    if session is None:
        session = Driver.DBSession()
    # docs = Driver.select(TrainingSet.doc_ids, TrainingSet.set_id == set_id).fetchone()[0]
    docs = session.query(TrainingSet.doc_ids).filter(TrainingSet.set_id == set_id).one().doc_ids

    rubrication_result = session.query(RubricationResult.doc_id, RubricationResult.result,
                                       RubricationResult.probability).filter(
        (RubricationResult.model_id == model_id) &
        (RubricationResult.rubric_id == rubric_id) &
        (RubricationResult.doc_id.in_(docs))).all()
    result = {}
    for doc_id in rubrication_result:
        result[str(doc_id[0])] = doc_id[result_type]
    return result


def put_gazetteer(name, lemmas, short_name='', session=None, commit_session=True):
    """write gazetteer in db"""
    if session is None:
        session = Driver.DBSession()
    new_gaz = Gazetteer(name=name)
    new_gaz.lemmas = lemmas
    new_gaz.gaz_id = name if short_name == '' else short_name
    session.add(new_gaz)
    if commit_session:
        session.commit()
    return new_gaz.gaz_id


def get_gazetteer(gaz_id, session=None):
    """read gazetteer from db"""
    if session is None:
        session = Driver.DBSession()
    return session.query(Gazetteer.lemmas).filter(Gazetteer.gaz_id == gaz_id).one().lemmas


def put_ner_feature(doc_id, records, feature_type, feature=None, session=None, commit_session=True):
    """write features of lemmas of document doc_id in db. records is list"""
    if session is None:
        session = Driver.DBSession()
    if feature is None:
        session.query(NERFeature).filter((NERFeature.doc_id == doc_id) &
                                     (NERFeature.feature_type == feature_type)).delete()
    else:
        session.query(NERFeature).filter((NERFeature.doc_id == doc_id) &
                                         (NERFeature.feature_type == feature_type) &
                                         (NERFeature.feature == feature)).delete()

    for record in records:
        new_feature = NERFeature(doc_id=doc_id, feature_type=feature_type, word_index=record['word_index'],
                                 sentence_index=record['sentence_index'], value=record['value'])
        # print(new_feature.value)
        # print(record['feature'], feature if not (feature is None) else record['feature'])
        new_feature.feature = feature if not (feature is None) else record['feature']
        session.add(new_feature)
    if commit_session:
        session.commit()


def put_ner_feature_dict(doc_id, records, feature_type, feature=None, session=None, commit_session=True):
    """write features of lemmas of document doc_id in db. records is dictionary"""
    if session is None:
        session = Driver.DBSession()
    if feature is None:
        session.query(NERFeature).filter((NERFeature.doc_id == doc_id) &
                                         (NERFeature.feature_type == feature_type)).delete()
    else:
        session.query(NERFeature).filter((NERFeature.doc_id == doc_id) &
                                         (NERFeature.feature_type == feature_type) &
                                         (NERFeature.feature == feature)).delete()

    for key in records:
        new_feature = NERFeature(doc_id=doc_id, feature_type=feature_type, word_index=key[1],
                                 sentence_index=key[0], value=records[key])
        # print(new_feature.value)
        # print(record['feature'], feature if not (feature is None) else record['feature'])
        new_feature.feature = feature if not (feature is None) else key[2]
        session.add(new_feature)
    if commit_session:
        session.commit()


def get_ner_feature(doc_id, session=None):
    """read lemmas features for document"""
    if session is None:
        session = Driver.DBSession()
    result_query = session.query(NERFeature).filter((NERFeature.doc_id == doc_id)).all()
    result = {}
    for i in result_query:
        # result.append({'sentence_index': i.sentence_index, 'word_index': i.word_index,
        #                'feature': i.feature, 'value': i.value})
        result[(i.sentence_index, i.word_index, i.feature)] = i.value
    return result


def get_ner_feature_for_set_dict(set_id, feature=None):
    """read lemmas features for documents in set. return {'doc_id_1':{(n,m):value, ...}, ...}"""
    return get_ner_feature_for_set(set_id, feature, True)


def get_ner_feature_for_set(set_id, feature=None, return_dict=False, session=None):
    """read lemmas features for documents in set. return {'doc_id_1':[(n,m,value), ...], ...}"""
    if session is None:
        session = Driver.DBSession()
    training_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    all_words = session.query(NERFeature).filter(
        NERFeature.doc_id.in_(training_set.doc_ids) & (NERFeature.feature == feature)).order_by(
        NERFeature.sentence_index, NERFeature.word_index).all()
    result = {}
    for word in all_words:
        doc_id = str(word.doc_id)
        if return_dict:
            if result.get(doc_id, None) is None:
                result[doc_id] = {}
            result[doc_id][(word.sentence_index, word.word_index)] = word.value
        else:
            if result.get(doc_id, None) is None:
                result[doc_id] = []
            result[doc_id].append((word.sentence_index, word.word_index, word.value))

    return result


def put_tomita_result(doc_id, grammar, result, session=None, commit_session=True):
    """write Tomita result with symbol coordinates for document"""
    if session is None:
        session = Driver.DBSession()
    session.query(TomitaResult).filter((TomitaResult.doc_id == doc_id) & (TomitaResult.grammar == grammar)).delete()
    session.add(TomitaResult(doc_id=doc_id, grammar=grammar, result=result))
    if commit_session:
        session.commit()


def get_tomita_results(doc_id, grammars, session=None):
    """read Tomita result with symbol coordinates for document"""
    if session is None:
        session = Driver.DBSession()
    # grammars - list of grammar
    res = session.query(TomitaResult.result).filter(
        (TomitaResult.doc_id == doc_id) & (TomitaResult.grammar.in_(grammars))).all()
    return [i[0] for i in res]


def put_markup(doc, doc_id, name, classes, markup_type, refs, session=None, commit_session=True):
    """write markup with references with symbol coordinates in db"""
    if session is None:
        session = Driver.DBSession()
    new_markup = Markup(document=doc_id, name=name, entity_classes=classes, type=markup_type)
    new_markup.markup_id = uuid.uuid4()
    session.add(new_markup)

    markup_for_doc = {}
    entities = {}
    for ref in refs:
        ref_id = str(uuid.uuid1())
        markup_for_doc[ref_id] = {'set': str(new_markup.markup_id),
                                  'class': ref['entity_class'],
                                  'entity': ref['entity'],
                                  'start_offset': ref['start_offset'],
                                  'end_offset': ref['end_offset'],
                                  'len_offset': ref['len_offset']}
        session.add(Reference(reference_id=ref_id, markup=new_markup.markup_id, entity_class=ref['entity_class'],
                              entity=ref['entity'], start_offset=ref['start_offset'], end_offset=ref['end_offset']))
        entities[ref['entity']] = ''
    doc.markup = markup_for_doc
    doc.entity_ids = entities.keys()
    if commit_session:
        session.commit()


def get_references_for_set(set_id, markup_type='10', session=None):
    """read references with symbol coordinates and entity class"""
    if session is None:
        session = Driver.DBSession()
    training_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
    all_refs = session.query(Reference, Markup).join(Markup).filter(
            Markup.document.in_(training_set.doc_ids) & (Markup.type == markup_type)).order_by(Reference.start_offset).all()
    result = {}
    for ref in all_refs:
        doc_id = str(ref[1].document)
        if result.get(doc_id, None) is None:
            result[doc_id] = []
        result[doc_id].append((ref[0].start_offset, ref[0].end_offset, ref[0].entity_class))
    return result


def get_multi_word_embedding(embedding, lemmas, session=None):
    """read embeddings for lemmas"""
    if session is None:
        session = Driver.DBSession()
    res = session.query(WordEmbedding).filter(
        (WordEmbedding.embedding == embedding) & (WordEmbedding.lemma.in_(lemmas))).all()
    if res is None:
        return None
    else:
        return {i.lemma: np.array(i.vector) for i in res}


# NO USED

# reading document plain text from db
def get_doc(doc_id, session=None):
    if session is None:
        session = Driver.DBSession()
    return session.query(Document.stripped).filter(Document.doc_id == doc_id).one().stripped


# writing lemmas frequently of document in db
# def put_lemmas(doc_id, lemmas, new_status, session=None):
#     if session is None:
#         session = Driver.DBSession()
#     some_doc = session.query(Document).filter(Document.doc_id == doc_id).one()
#     some_doc.lemmas = lemmas
#     if new_status > 0:
#         some_doc.status = new_status
#     session.commit()


# reading lemmas frequently of document from db
def get_lemmas(doc_id, session=None):
    if session is None:
        session = Driver.DBSession()
    return session.query(Document.lemmas).filter(Document.doc_id == doc_id).one().lemmas


# reading lemmas frequently of document from db
def get_markup_from_doc(doc_id, session=None):
    if session is None:
        session = Driver.DBSession()
    return session.query(Document.markup).filter(Document.doc_id == doc_id).one().markup


# reading answer for one document and one rubric
def get_rubric_answer_doc(doc_id, rubric_id, session=None):
    if session is None:
        session = Driver.DBSession()
    doc_rubric = session.query(DocumentRubric.doc_id).filter(
        (DocumentRubric.rubric_id == rubric_id) & (DocumentRubric.doc_id == doc_id)).all()
    return len(doc_rubric)


# text of all documents in set
def get_docs_text(set_id, session=None):
    if session is None:
        session = Driver.DBSession()
    docs_id = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one().doc_ids
    docs = session.query(Document.doc_id, Document.stripped, Document.morpho, Document.lemmas).filter(
        (DocumentRubric.doc_id.in_(docs_id))).all()

    result = {}
    for doc in docs:
        result[str(doc.doc_id)] = {'text': doc.stripped, 'morpho': doc.morpho, 'lemmas': doc.lemmas}
    return result



def del_markup(markup_id=None, markup_type=None, session=None, commit_session=True):
    if session is None:
        session = Driver.DBSession()
    if markup_id is None:
        markups = session.query(Markup.markup_id).filter(Markup.type == markup_type).all()
        markup_ids = [i[0] for i in markups]
    else:
        markup_ids = [markup_id]
    for m_id in markup_ids:
        session.query(Reference).filter(Reference.markup == m_id).delete()
        session.query(Markup).filter(Markup.markup_id == m_id).delete()
    session.commit()


def get_word_embedding(embedding, lemma, session=None):
    if session is None:
        session = Driver.DBSession()
    res = session.query(WordEmbedding.vector).filter(
        (WordEmbedding.embedding == embedding) & (WordEmbedding.lemma == lemma)).first()
    if res is None:
        return None
    else:
        return res[0]


def put_tomita_grammar(name, files, config_file, session=None, commit_session=True):
    if session is None:
        session = Driver.DBSession()
    new_grammar = TomitaGrammar(name=name, files=files, config_file=config_file)
    session.add(new_grammar)
    session.commit()


def put_ner_model(embedding, gazetteers, tomita_facts, morpho_features, hyper_parameters, session=None, commit_session=True):
    if session is None:
        session = Driver.DBSession()
    new_model = NERModel(embedding=embedding, gazetteers=gazetteers, tomita_facts=tomita_facts,
                         morpho_features=morpho_features, hyper_parameters=hyper_parameters)
    session.add(new_model)
    session.commit()
    return new_model.ner_id


def get_ner_model(model_id, session=None):
    if session is None:
        session = Driver.DBSession()
    model = session.query(NERModel).filter(NERModel.ner_id == model_id).one()
    return {'embedding': model.embedding, 'gazetteers': model.gazetteers, 'tomita_facts': model.tomita_facts,
            'morpho_features': model.morpho_features, 'hyper_parameters': model.hyper_parameters}
