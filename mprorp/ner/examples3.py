import mprorp.ner.NER as NER
from mprorp.ner.NER import sets
import os
import mprorp.db.dbDriver as Driver
from mprorp.db.models import Document
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
from mprorp.ner.set_list import set_temp
from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.tomita.tomita_run import run_tomita2
import mprorp.ner.feature as ner_feature
from mprorp.ner.identification import create_answers_feature_for_doc
from mprorp.ner.identification import create_answers_span_feature_for_doc
from mprorp.db.models import *
from mprorp.ner.identification import create_markup_regular
from mprorp.utils import home_dir
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup
import mprorp.ner.feature as feature
import random
import mprorp.ner.set_list as set_list

session = Driver.db_session()
# 1. Create sets: training and dev
# Создание учебной и тестовой выборок для каждого класса, исходя из наличия этого класса в mentions.entity_class:
# Если нужный нам класс указан в entity_class, то мы берем соответствующий markup, получаем из него document и все,
# найденные таким оразом, документы складываем в выборки: учебную и тестовую
# sets = {"oc_class_org": {}, "oc_class_loc": {}}

# sets = dict()

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
# sets['oc_class_person'] = {'train': '4fb42fd1-a0cf-4f39-9206-029255115d01',
#                            'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}

# sets['name'] = {'train': '3a21671e-5ac0-478e-ba14-3bb0ac3059e3', # '2e366853-4533-4bd5-a66e-92a834a1a2ca'
#                 'dev': '375fa594-6c76-4f82-84f0-9123b89307c4'}

# огромные выборки: 29313 и 7328
# sets['name'] = {'train': '5fc21192-9a45-41b1-bf6b-df75877b60eb', # '2e366853-4533-4bd5-a66e-92a834a1a2ca'
#                 'dev': '5684de0c-c6a1-43ef-b004-daefeeaf5e4a'}

# огромные выборки: 29774 и 7443
# sets['name'] = {'train': '6bdc99ea-0176-4892-954d-d89ae8d253d3', # '2e366853-4533-4bd5-a66e-92a834a1a2ca'
#                 'dev': 'a067d48c-4da4-4f7d-a116-0f11add07275'}



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

NER_settings = {"class": 1, "tags": 1, "use_special_tags": 0}

filename_part = str(NER_settings['class']
                    ) + '_' + str(NER_settings['tags']
                    ) + '_' + str(NER_settings['use_special_tags'])
filename_tf = home_dir + '/weights/ner_oc_' + filename_part + '.weights'
filename_params = home_dir + '/weights/ner_oc_' + filename_part + '.params'


def create_sets(cl, markup_type='51', doc_number=None):
    docs = db.get_docs_for_entity_class(cl, markup_type=markup_type, session=session)
    random.shuffle(docs)
    if doc_number is None:
        doc_number = len(docs)
    train_num = round(doc_number * 0.8)
    sets[cl]['train'] = str(db.put_training_set(docs[:train_num]))
    sets[cl]['dev'] = str(db.put_training_set(docs[train_num:doc_number]))
    print(sets)


def create_sets_56(markup_type='56', doc_number=1000):
    docs = db.get_docs_by_markup_type(markup_type=markup_type, session=session)
    random.shuffle(docs)
    start_num = 0
    print('sets size', doc_number)
    while start_num + doc_number < len(docs):
        set_train = str(db.put_training_set(docs[start_num:start_num + doc_number]))
        start_num += doc_number
        print(set_train)
    set_train = str(db.put_training_set(docs[start_num:]))
    print(set_train)
    print('last set size', len(docs[start_num:]))



# def set_without_doc(set_id, doc_id):


def morpho():
    # 2. morpho and other steps for docs from sets
    count = 0
    for cl in set_docs:
        for set_type in set_docs[cl]:
            for doc_id in set_docs[cl][set_type]:
                if count % 100 == 0:
                    print(count)
                count += 1
                if count < 1500:
                    continue
                rb.morpho_doc2(str(doc_id))
    print('morpho - done')


def morpho_with_check(doc_list):
    count = 0
    bad_list = []
    for doc_id in doc_list:

        try:
            doc = session.query(Document).filter_by(doc_id=doc_id).first()
            if doc.morpho is None:
                rb.morpho_doc(doc)
                session.commit()
        except:
            bad_list.append(doc_id)
    return bad_list


def capital_embedding_morpho_feature(doc_list, start_doc=0):
    count = 0
    bad_list = []
    for doc_id in doc_list[start_doc:]:

        # try:
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        ner_feature.create_capital_feature(doc, session=session, commit_session=False)
        ner_feature.create_embedding_feature(doc, session=session, commit_session=False)
        ner_feature.create_morpho_feature(doc,session=session, commit_session=False)
        session.commit()
        # except:
        #     bad_list.append(doc_id)
        #     print('except:', doc_id)
    return bad_list


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


def tomita(doc_list, num_set=0, first_doc = 0):
    my_count = 0
    for doc_id in doc_list:
        if my_count < first_doc:
            my_count += 1
            continue
        print(num_set, my_count, doc_id)
        for gram in grammar_config:
            run_tomita2(gram, str(doc_id))
        print('tomita - ok')
        ner_feature.create_tomita_feature2(str(doc_id), grammar_config.keys())
        print('tomita feature - ok')
        my_count += 1
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


def create_big_set_name_answers(doc_list, spans, cl='name'):
    count = 0
    bad_list = set()
    not_found_docs = []
    for doc_id in doc_list:
        count += 1
        # if count > 500:
        #     break
        if count%100 == 0:
            print(count)
        try:
            doc = session.query(Document).filter_by(doc_id=doc_id).first()
        except:
            not_found_docs.append(doc_id)
            # print('doc not found')
            continue
        # print(doc.stripped)
        if doc is None:
            not_found_docs.append(doc_id)
            # print('doc not found')
            continue
        # create_answers_span_feature_for_doc(doc, ['name', 'surname'], bad_list=bad_list)
        create_answers_span_feature_for_doc(doc, spans=spans, bad_list=bad_list,
                                            ner_feature_name=cl+'_answers', cl=cl, verbose=True)
    print('not found docs:', not_found_docs)
    print('docs with zero chains:', list(bad_list))


def learning():
    # 4. Обучение и запись модели в файл
    if not os.path.exists(home_dir + "/weights"):
        os.makedirs(home_dir + "/weights")

    NER_config = NER.Config()
    NER_config.learn_type = NER_settings

    learn_class = NER_config.classes[NER_config.learn_type['class']]
    NER_config.feature_type = feature.ner_feature_types[learn_class + '_answers']
    NER_config.feature_answer = [learn_class + '_' + i for i in NER_config.tag_types[NER_config.learn_type['tags']]]

    NER_config.training_set = sets[learn_class]['train']
    NER_config.dev_set = sets[learn_class]['dev']

    print(NER_config.feature_answer)

    NER.NER_learning(filename_params, filename_tf, NER_config)


def prediction(learn_class):
    # 5. Prediction
    for doc_id in set_docs[learn_class]['dev']:
        values = {}
        doc = session.query(Document).filter_by(doc_id=doc_id).first()

        NER.NER_predict(doc, [{"class": 1, "tags": 1, "use_special_tags": 0}],
                        session, commit_session=False, verbose=True)
        # NER.NER_predict_set(doc, filename_params, filename_tf, values, session, verbose=True)
        # print(values)
        # if len(values) > 0:
        #     db.put_ner_feature_dict(doc.doc_id, values, feature.ner_feature_types[learn_class + '_predictions'],
        #                             session=session)
    session.commit()


def comparison():
    # 6. Comparison

    compar = dict()
    NER_config = NER.Config()
    NER_config.learn_type = NER_settings

    learn_class = NER_config.classes[NER_config.learn_type['class']]
    NER_config.feature_type = feature.ner_feature_types[learn_class + '_answers']
    NER_config.feature_answer = [learn_class + '_' + i for i in NER_config.tag_types[NER_config.learn_type['tags']]]

    NER_config.training_set = sets[learn_class]['train']
    NER_config.dev_set = sets[learn_class]['dev']

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
    # print(answers)
    # print(predict)
    for doc_id in answers:
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        # print(doc.stripped)
        # print('Слово, правильный ответ, предсказание')
        # diff = {}
        # if predict.get(doc_id, None) is None:
        #     predict[doc_id] = {}
        # if tomita_loc.get(doc_id, None) is None:
        #     tomita_loc[doc_id] = {}
        all_keys = set()
        for key in answers[doc_id]:
            all_keys.add(key)
            # if predict[doc_id].get(key, None) != answers[doc_id][key]:
            #     add_difference(diff, key, answers[doc_id][key], predict[doc_id].get(key, None), tomita_loc[doc_id].get(key, None))
        for key in predict[doc_id]:
            all_keys.add(key)
            # if answers[doc_id].get(key, None) is None:
            #     add_difference(diff, key, None, predict[doc_id][key], tomita_loc[doc_id].get(key, None))
        for key in all_keys:
            pred = predict[doc_id].get(key, None)
            ans = answers[doc_id].get(key, None)
            if pred is not None:
                if compar.get(pred, None) is None:
                    compar[pred] = {'t_p': 0, 't_n': 0, 'f_p': 0, 'f_n': 0}
                if pred == ans:
                    compar[pred]['t_p'] += 1
                else:
                    compar[pred]['f_p'] += 1
            elif ans is not None:
                if compar.get(ans, None) is None:
                    compar[ans] = {'t_p': 0, 't_n': 0, 'f_p': 0, 'f_n': 0}
                compar[ans]['f_n'] += 1
    print(compar)


        # for elem in doc.morpho:
        #     sent_i = elem.get('sentence_index', None)
        #     if sent_i is not None and sent_i in diff:
        #         if elem['word_index'] in diff[sent_i]:
        #             print(elem['text'], diff[sent_i][elem['word_index']])


def add_difference(diff, key, ans, pred, add_feature=None):
    if key[0] not in diff:
        diff[key[0]] = {}
    if add_feature is None:
        diff[key[0]][key[1]] = (ans, pred)
    else:
        diff[key[0]][key[1]] = (ans, pred, add_feature)


def identification(learn_class):
    # 7. Identification
    settings_list = {
        'identification_settings': {"identification_type": 1, "tag_type": ["BS", "IE"], "learn_class": "name"},
        'name': 'from NER',
        'markup_type': '20'
    }
    number = 0
    for doc_id in set_docs[learn_class]['dev']:
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        print(doc.stripped)
        create_markup_regular(doc, settings_list, verbose=True)
        number += 1
        if number == 10:
            exit()


def identification_doc(doc_id):
    # settings_list = {
    #     'identification_settings': [{"identification_type": 1, "tag_type": ["BS", "IE"], "learn_class": "name",
    #                                  "create_new_entities": False, "create_wiki_entities": False,
    #                                  "add_conditions": {"external_data": {"has_key": ["pp_id"]}}
    #      }],
    #     'name': 'from NER',
    #     'markup_type': '20'
    # }
    settings_list = {
        'identification_settings': [{"identification_type": 1, "tag_type": ["BS", "IE"], "learn_class": "name"}],
        'name': 'from NER',
        'markup_type': '20'
    }

    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    # print(doc.stripped)
    create_markup_regular(doc, settings_list, verbose=True)


def get_doc_id(rec_id):
    res = session.query(Record.source).filter_by(document_id=rec_id).first()
    return str(res[0])


def script_exec():

    # my_list = list(db.get_set_docs(set_list.set_temp['1700']))
    # my_list.extend(list(db.get_set_docs(set_list.sets1250[4])))
    # my_list.extend(list(db.get_set_docs(set_list.sets1250[5]))[0:450])
    # print('3400', db.put_training_set(my_list))
    # my_list = list(db.get_set_docs(set_list.set_temp['300']))
    # my_list.extend(list(db.get_set_docs(set_list.sets1250[5]))[450:750])
    # print('600',  db.put_training_set(my_list))
    # exit()


    # create_sets_56(doc_number=100)
    # exit()
    # bad_list = set_docs['name']['train']
    set_list_len = len(set_list.sets1250)
    # print('start morpho')
    # for count in range(set_list_len):
    #     print('count', count)
    #     bad_list = db.get_set_docs(set_list.sets1250[count])
    #     past_count = 0
    #     while (len(bad_list) > 0) and (len(bad_list) != past_count):
    #         past_count = len(bad_list)
    #         bad_list = morpho_with_check(bad_list)
    #         print('morpho tried for', past_count, 'rest', len(bad_list))

    # print('start features')
    # start_num = 22
    # for count in range(start_num, set_list_len):
    #     print('count', count)
    #     bad_list = db.get_set_docs(set_list.sets1250[count])
    #     past_count = 0
    #     while (len(bad_list) > 0) and (len(bad_list) != past_count):
    #         past_count = len(bad_list)
    #         bad_list = capital_embedding_morpho_feature(bad_list)
    #         print('features tried for', past_count, 'rest', len(bad_list))
    #
    # print('start answers')
    # for count in range(set_list_len):
    #     print('count', count)
    #     doc_list = db.get_set_docs(set_list.sets1250[count])
    #     # create_big_set_name_answers(doc_list, ['bs000_loc_descr', 'bs000_loc_name'], 'loc')
    #     create_big_set_name_answers(doc_list, ['bs000_name', 'bs000_surname'], 'name')
    #
    # print('start tomita')
    #
    # for count in range(3, set_list_len):
    #     print('count', count)
    #     doc_list = db.get_set_docs(set_list.sets1250[count])
    #     # create_big_set_name_answers(doc_list, ['bs000_loc_descr', 'bs000_loc_name'], 'loc')
    #     first = [487, 405, 1090]
    #     tomita(doc_list, count, 0 if len(first) <= count else first[count])
    # exit()
    NER.NER_learning_by_config({"class": 1, "tags": 1, "use_special_tags": 0})
    exit()
    # exit()
    # create_answers('oc_class_loc')
    # prediction('name')
    rec_set = ['d1b44788-bfb6-36b2-d001-713af427127c',
               '756c27e4-3036-aed7-6b3b-8813dc00352a',
               'a43dc00b-f780-0937-76e1-d685fbd3c322',
               '1f3f9f95-d24b-b63a-ff34-9b7eb6f75656']
    rec_set = ['5063bc12-df66-98b9-0342-84b3e41691a8']
    doc_set = ['7232cfa3-a820-4c2f-b186-c57e58db2bb7',
               '177097e8-0e9e-4392-a586-7bb0c4dfe2c9',
               '68870091-58cb-4719-9089-5da62398ce65',
               '31f8194a-b292-4d52-a6ca-27bb1cec5da2']
    # rec_set = db.get_set_docs(sets['name']['dev'])
    # doc_set = ['664db67f-cc86-4933-82c0-20a555a38281']
    doc_set = []
    for rec_id in rec_set:
        doc_set.append(get_doc_id(rec_id))

    # for doc_id in doc_set:
    #     doc = session.query(Document).filter_by(doc_id=doc_id).first()
    #     rb.morpho_doc(doc)
    # session.commit()
    capital_embedding_morpho_feature(doc_set)

    for doc_id in doc_set:
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        if doc is None:
            print('No document', doc_id)
        print(doc.stripped)
        print('Morpho', doc.morpho)
        NER.NER_predict(doc, [{"class": 1, "tags": 1, "use_special_tags": 0}],
                        session, commit_session=True, verbose=True)
        identification_doc(doc_id)
    # comparison()
    # 756c27e4-3036-aed7-6b3b-8813dc00352a
    # a43dc00b-f780-0937-76e1-d685fbd3c322
    # 1f3f9f95-d24b-b63a-ff34-9b7eb6f75656
    # doc_id = 'f98e75ea-feee-480d-80cc-fe5b4a21e727'
    # print(db.get_doc_text(doc_id))
    # print(doc_id)
    # prediction('name')
    # identification_doc(doc_id)
    # comparison()
    # set_t = set(set_docs['name']['train'])
    # set_d = set(set_docs['name']['dev'])
    # print(len(set_d), len(set_t), len(set_d & set_t))

    # NER.NER_name_learning()

    # db.delete_entity('b7f4eedd-ba7f-422b-9299-e43c414ceb1e') #'347f1317-eb2a-4a4b-af76-f9c2f2bd1fa9')
    # print(db.get_entity_by_labels(['Алексей'], verbose=True))

script_exec()


