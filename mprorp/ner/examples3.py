import mprorp.ner.NER as NER
import os
import mprorp.db.dbDriver as Driver
from mprorp.db.models import Document
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.tomita.tomita_run import run_tomita2
import mprorp.ner.feature as ner_feature
from mprorp.ner.identification import create_answers_feature_for_doc
from mprorp.db.models import *
from mprorp.ner.identification import create_markup_name
from mprorp.utils import home_dir
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup
import mprorp.ner.feature as feature
import random

session = Driver.db_session()
# 1. Create sets: training and dev
# Создание учебной и тестовой выборок для каждого класса, исходя из наличия этого класса в mentions.entity_class:
# Если нужный нам класс указан в entity_class, то мы берем соответствующий markup, получаем из него document и все,
# найденные таким оразом, документы складываем в выборки: учебную и тестовую
# sets = {"oc_class_org": {}, "oc_class_loc": {}}

sets = dict()

# sets for database 139.162.170.98
# sets['oc_class_person'] = {'train': '2e366853-4533-4bd5-a66e-92a834a1a2ca',
#                            'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}
#
# sets['name'] = {'train': '2e366853-4533-4bd5-a66e-92a834a1a2ca',
#                 'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}
#
# sets['oc_class_org'] = {'train': '78f8c9fb-e385-442e-93b4-aa1a18e952d0',
#                         'dev': '299c8bd1-4e39-431d-afa9-398b2fb23f69'}
# sets['oc_class_loc'] = {'train': '74210e3e-0127-4b21-b4b7-0b55855ca02e',
#                         'dev':  '352df6b5-7659-4f8c-a68d-364400a5f0da'}
# sets['oc_class_loc'] = {'train': '9a9f7fdf-af69-439c-b30e-7e237a8cd037',
#                         'dev': 'cff51852-6d37-4873-bef5-4d088b50a0a3'}

# set for database 46.101.162.206
sets['oc_class_person'] = {'train': '2e366853-4533-4bd5-a66e-92a834a1a2ca',
                           'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}

sets['name'] = {'train': '4fb42fd1-a0cf-4f39-9206-029255115d01',
                'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}

# sets['oc_class_org'] = {'train': '78f8c9fb-e385-442e-93b4-aa1a18e952d0',
#                         'dev': '299c8bd1-4e39-431d-afa9-398b2fb23f69'}
# sets['oc_class_loc'] = {'train': '74210e3e-0127-4b21-b4b7-0b55855ca02e',
#                         'dev': '352df6b5-7659-4f8c-a68d-364400a5f0da'}
# sets['oc_class_loc'] = {'train': '9a9f7fdf-af69-439c-b30e-7e237a8cd037',
#                         'dev': 'cff51852-6d37-4873-bef5-4d088b50a0a3'}

set_docs = {}
for cl in sets:
    set_docs[cl] = {}
    for set_type in sets[cl]:
        set_docs[cl][set_type] = db.get_set_docs(sets[cl][set_type])
        print(cl, set_type, len(set_docs[cl][set_type]), 'documents')

if not os.path.exists(home_dir + "/weights"):
    os.makedirs(home_dir + "/weights")

NER_config = NER.Config()
learn_class = NER_config.classes[NER_config.learn_type['class']]
NER_config.feature_type = feature.ner_feature_types[learn_class + '_answers']
NER_config.feature_answer = [learn_class + '_' + i for i in NER_config.tag_types[NER_config.learn_type['tags']]]
filename_part = str(NER_config.learn_type['class']) + '_' + str(NER_config.learn_type['tags'])
filename_tf = home_dir + '/weights/ner_oc_' + filename_part + '.weights'
filename_params = home_dir + '/weights/ner_oc_' + filename_part + '.params'


def create_sets(cl):
    docs = db.get_docs_for_entity_class(cl, markup_type='51', session=session)
    random.shuffle(docs)
    train_num = round(len(docs) * 0.8)
    sets[cl]['train'] = str(db.put_training_set(docs[:train_num]))
    sets[cl]['dev'] = str(db.put_training_set(docs[train_num:len(docs)]))
    print(sets)


def morpho():
    # 2. morpho and other steps for docs from sets

    for cl in set_docs:
        for set_type in set_docs[cl]:
            for doc_id in set_docs[cl][set_type]:
                rb.morpho_doc2(str(doc_id))
    print('morpho - done')


def capital():
    for cl in set_docs:
        for set_type in set_docs[cl]:
            for doc_id in set_docs[cl][set_type]:
                ner_feature.create_capital_feature2(doc_id)
    print('capital - done')


def embedding():

    for cl in set_docs:
        for set_type in set_docs[cl]:
            for doc_id in set_docs[cl][set_type]:
                ner_feature.create_embedding_feature2(str(doc_id))
    print('embedding feature - done')


def morpho_feature():

    for cl in set_docs:
        for set_type in set_docs[cl]:
            for doc_id in set_docs[cl][set_type]:
                ner_feature.create_morpho_feature2(str(doc_id))
    print('morpho feature - done')


def tomita():
    for cl in set_docs:
        for set_type in set_docs[cl]:
            for doc_id in set_docs[cl][set_type]:
                for gram in grammar_config:
                    run_tomita2(gram, str(doc_id))
                ner_feature.create_tomita_feature2(str(doc_id), grammar_config.keys())
    print('tomita - done')


def create_answers(cla=None):
    # 3. Create answers for docs
    if cla is None:
        class_list = list(set_docs.keys())
    else:
        class_list = [cla]
    for cl in class_list:
        for set_type in set_docs[cl]:
            for doc_id in set_docs[cl][set_type]:
                doc = session.query(Document).filter_by(doc_id=doc_id).first()
                create_answers_feature_for_doc(doc, cl, verbose=True)
    session.commit()


def learning():
    # 4. Обучение и запись модели в файл
    if not os.path.exists(home_dir + "/weights"):
        os.makedirs(home_dir + "/weights")

    NER_config.training_set = sets[learn_class]['train']
    NER_config.dev_set = sets[learn_class]['dev']

    print(NER_config.feature_answer)

    NER.NER_learning(filename_params, filename_tf, NER_config)


def prediction():
    # 5. Prediction
    for doc_id in set_docs[learn_class]['dev']:
        values = {}
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        NER.NER_predict_set(doc, filename_params, filename_tf, values, session, verbose=True)
        print(values)
        if len(values) > 0:
            db.put_ner_feature_dict(doc.doc_id, values, feature.ner_feature_types[learn_class + '_predictions'],
                                    session=session)
    session.commit()


def comparison():
    # 6. Comparison

    dev_set = sets[learn_class]['dev']
    answers_type = feature.ner_feature_types[learn_class + '_answers']
    predict_type = feature.ner_feature_types[learn_class + '_predictions']
    tomita_type = feature.ner_feature_types['tomita']
    answers = db.get_ner_feature_dict(set_id=dev_set, feature_type=answers_type,
                                            feature_list=NER_config.feature_answer)
    predict = db.get_ner_feature_dict(set_id=dev_set, feature_type=predict_type,
                                            feature_list=NER_config.feature_answer)
    tomita_loc = db.get_ner_feature_dict(set_id=dev_set, feature_type=tomita_type,
                                            feature_list=['Loc'])
    print(answers)
    print(predict)
    for doc_id in answers:
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        print(doc.stripped)
        print('Слово, правильный ответ, предсказание')
        diff = {}
        if predict.get(doc_id, None) is None:
            predict[doc_id] = {}
        if tomita_loc.get(doc_id, None) is None:
            tomita_loc[doc_id] = {}
        for key in answers[doc_id]:
            if predict[doc_id].get(key, None) != answers[doc_id][key]:
                add_difference(diff, key, answers[doc_id][key], predict[doc_id].get(key, None), tomita_loc[doc_id].get(key, None))
        for key in predict[doc_id]:
            if answers[doc_id].get(key, None) is None:
                add_difference(diff, key, None, predict[doc_id][key], tomita_loc[doc_id].get(key, None))
        for elem in doc.morpho:
            sent_i = elem.get('sentence_index', None)
            if sent_i is not None and sent_i in diff:
                if elem['word_index'] in diff[sent_i]:
                    print(elem['text'], diff[sent_i][elem['word_index']])


def add_difference(diff, key, ans, pred, add_feature=None):
    if key[0] not in diff:
        diff[key[0]] = {}
    if add_feature is None:
        diff[key[0]][key[1]] = (ans, pred)
    else:
        diff[key[0]][key[1]] = (ans, pred, add_feature)


def identification():
    # 7. Identification
    number = 0
    for doc_id in set_docs[learn_class]['dev']:
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        print(doc.stripped)
        create_markup_name(doc, verbose=True)
        number += 1
        if number == 10:
            exit()


def script_exec():
    # create_sets('oc_class_person')
    # learning()
    # create_answers('oc_class_loc')
    prediction()
    identification()
    # prediction()
    # comparison()

    NER.NER_name_learning()

script_exec()