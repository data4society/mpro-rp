import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
import random
from mprorp.ner.set_list import sets, rubrics, rubric_names

rubric_no_name = '35ed00df-3be5-4533-9f13-7535a95dba62'


def create_training_set(rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    new_docs = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=1200).all()
    ids = []
    free = []
    for doc in new_docs:
        if rubric_id in str(doc.rubric_ids):
            ids.append(doc.doc_id)
        else:
            free.append(doc.doc_id)
    max_len = min(len(ids), len(free))
    b = (max_len // 5) * 4
    tr_set_t = ids[:b]
    tr_set_f = free[:b]
    test_set_t = ids[b:max_len]
    test_set_f = free[b:max_len]

    print('Создание выборки по рубрике ' + rubric_id)
    print('всего положительных и отрицательных документов есть по ', max_len)
    print('в учебную выборку возьмем по ', b)
    print('в учебной выборке получилось ', len(tr_set_t) + len(tr_set_f), ' документов')
    print('в тестовой выборке получилось ', len(test_set_t) + len(test_set_f), ' документов')

    # free_docs = session.query(Document).filter_by(rubric_ids=None, status=1200)[:b]
    # for doc in free_docs:
    #  tr_set.append(doc.doc_id)
    # free_docs = session.query(Document).filter_by(rubric_ids=None, status=1200)[b:b+len(test_set)]
    # for doc in free_docs:
    #     test_set.append(doc.doc_id)
    return [tr_set_t, tr_set_f, test_set_t, test_set_f]


def add_rubric_to_doc_1200(rubric_id, session=None):
    print('Отмечаем рубрики документов в таблице')
    if session is None:
        session = Driver.db_session()

    new_docs = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=1200).all()
    print('Всего документов со статусом 1200: ', len(new_docs))
    count = 0
    for doc in new_docs:
        session.query(DocumentRubric).filter(
            (DocumentRubric.doc_id == doc.doc_id) & (DocumentRubric.rubric_id == rubric_id)).delete()
        if rubric_id in str(doc.rubric_ids):
            new_id = DocumentRubric(doc_id=doc.doc_id, rubric_id=rubric_id)
            session.add(new_id)
            count +=1

    session.commit()
    print('Из них ', count, ' относятся к рубрике и добавлены в таблицу')


def write_sets(rubric_id, session=None):
    sets = create_training_set(rubric_id)
    tr_set_t = sets[0]
    tr_set_f = sets[1]
    test_set_t = sets[2]
    test_set_f = sets[3]

    tr_set = tr_set_t
    tr_set.extend(tr_set_f)
    test_set = test_set_t
    test_set.extend(test_set_f)

    if session is None:
        session = Driver.db_session()
    new_tr_set = TrainingSet(doc_ids=tr_set, doc_num=len(tr_set), name='Matvey_set_tr')
    session.add(new_tr_set)

    new_test_set = TrainingSet(doc_ids=test_set, doc_num=len(test_set), name='Matvey_set_tr')
    session.add(new_test_set)
    session.commit()
    return new_tr_set.set_id, new_test_set.set_id


def teach_rubricator(set_id, rubric_id, session=None, verbose=False):
    rb.idf_object_features_set(set_id, verbose=verbose)
    rb.learning_rubric_model(set_id, rubric_id, verbose=verbose)
    # rb.learning_rubric_model_coeffs(set_id, doc_coefficients, rubric_id, savefiles=False, verbose=verbose)


def test_model(set_id, rubric_id, tr_set=None, name=''):
    model_id = rb.spot_test_set_rubric(set_id, rubric_id, training_set_id=tr_set)
    print('При тестировании для рубрики ', rubric_id, ' использована модель ', model_id)
    # for doc_id in db.get_set_docs(set_id):
    #     rb.spot_doc_rubrics2(doc_id, {rubric_id: None}, verbose=True)
    # model_id = db.get_model(rubric_id)["model_id"]
    # if protocol != '':
    #     file_name = protocol + '_' + name + '.txt'
    result = rb.f1_score(model_id, set_id, rubric_id)
    return result


def prepare_docs(set_id):
    for doc_id in db.get_set_docs(set_id):
        rb.morpho_doc2(doc_id)
        rb.lemmas_freq_doc2(doc_id)


def do_exercise(rubric_id, name=''):

    add_rubric_to_doc_1200(rubric_id)
    if sets[rubric_id] is None:
        print('Создаем новые выборки')
        tr_id, test_id = write_sets(rubric_id)
        print('train set:', tr_id)
        print('test  set:', test_id)
    else:
        print('Используем существующие выборки')
        tr_id, test_id = sets[rubric_id]['train'], sets[rubric_id]['test']

    # add_rubric_to_doc(rubric_id)
    # prepare_docs(tr_id)
    # prepare_docs(test_id)
    # print('Предварительная обработка документов из обеих выборок завершена')

    # teach_rubricator(tr_id, rubric_id)
    # print('Обучение рубрикатора завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(tr_id, rubric_id, name=name))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_id, rubric_id, name=name))

# rubric_1 = '19848dd0-436a-11e6-beb8-9e71128cae21'
# rubric_2 = '19848dd0-436a-11e6-beb8-9e71128cae02'

# Новые большие выборки - октябрь 2016
# sets = {rubric_1: {'train': 'bcc7f879-8745-459f-8cda-963ae51fa878',
#                    'test':  'c8e1dbac-6a30-47f6-8a64-e383c748d559'},
#         rubric_2: {'train': '17620f74-bf7a-4467-b6cc-e11b8acd727d',
#                    'test':  'c3fabc6e-68c7-4a01-8ead-363dfab7b7e6'}}

# # Старые маленькие выборки - август 2016
# sets = {rubric_1: {'train': 'ced81603-5621-4391-9c5d-02044075cab8',
#                    'test':  'e51e4995-5c4f-48be-a23a-8b58f6854e2f'},
#         rubric_2: {'train': '5f76733a-e1f6-4ae4-8662-2915455cef53',
#                    'test':  '869df84f-8435-483b-87a0-9043f8703108'}}


def analyze_rubrics(rubric_1, rubric_2):
    session = Driver.db_session()
    new_docs = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=1200).all()
    rubrics = {}
    for doc in new_docs:
        if doc.rubric_ids is not None:
            for rubric in doc.rubric_ids:
                rubrics[str(rubric)] = rubrics.get(str(rubric), 0) + 1
    print(rubrics)
    print(rubrics.get(rubric_1, 0))
    print(rubrics.get(rubric_2, 0))
    docs_1 = session.query(DocumentRubric).filter_by(rubric_id=rubric_1).all()
    print(len(docs_1))
    docs_2 = session.query(DocumentRubric).filter_by(rubric_id=rubric_2).all()
    print(len(docs_2))


# analyze_rubrics(rubric_1, rubric_2)
# print('ассоциации')
# do_exercise(rubric_1, name='ассоциации') #свобода ассоциаций
# print('собрания')
# do_exercise(rubric_2, name='собрания') #свобода собраний

def add_rubric_to_docs(rubric_id, doc_ids, session=None):
    if session is None:
        session = Driver.db_session()
    for doc_id in doc_ids:
        session.query(DocumentRubric).filter((DocumentRubric.rubric_id == rubric_id) &
                                             (DocumentRubric.doc_id == doc_id)).delete()
        new_id = DocumentRubric(doc_id=doc_id, rubric_id=rubric_id)
        session.add(new_id)
    session.commit()


def create_sets(rubric_id, test_count=10):
    session = Driver.db_session()
    doc_ids_pos = db.get_moderated_docs(rubric_id)
    print('Найдено', len(doc_ids_pos), 'документов')
    add_rubric_to_docs(rubric_id, doc_ids_pos)
    random.shuffle(doc_ids_pos)
    set_pos_dev = db.put_training_set(doc_ids_pos[:test_count])
    set_pos_train = db.put_training_set(doc_ids_pos[test_count:])
    session.commit()
    return set_pos_train, set_pos_dev, doc_ids_pos[test_count:]


def give_name_to_sets(rub_num, version=''):
    set_num = version + rub_num
    print(set_num)
    session = Driver.db_session()
    for set_name in sets[set_num]:
        Tr_set = session.query(TrainingSet).filter(TrainingSet.set_id == sets[set_num][set_name]).one()
        new_set_name = rubric_names[rub_num] + '_' + set_name
        if version != '':
            new_set_name += '_' + version
        Tr_set.name = new_set_name
        print(rub_num, set_name, Tr_set.set_id, Tr_set.name)
    # Tr_set = session.query(TrainingSet).filter(TrainingSet.set_id == tr_com).one()
    # # Tr_set.name = 'tr_com'
    # print(Tr_set.set_id, Tr_set.name)
    # Tr_set = session.query(TrainingSet).filter(TrainingSet.set_id == tr_com100).one()
    # # Tr_set.name = 'tr_com100'
    # print(Tr_set.set_id, Tr_set.name)
    # Tr_set = session.query(TrainingSet).filter(TrainingSet.set_id == test_com).one()
    # # Tr_set.name = 'test_com'
    # print(Tr_set.set_id, Tr_set.name)
    session.commit()


def create_sets_polit_press(rubric_id, rubric_name, session=None):
    if session is None:
        session = Driver.db_session()
    negative_docs = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=71).all()
    print('neg', len(negative_docs))
    temp_list = []
    for doc in negative_docs:
        temp_list.append(str(doc.doc_id))
    train_len = round(len(temp_list) * .8)
    new_set_train = []
    new_set_test = []
    for i in temp_list[:train_len]:
        new_set_train.append(i)
    for i in temp_list[train_len:]:
        new_set_test.append(i)

    positive_docs = session.query(DocumentRubric.doc_id).filter_by(rubric_id=rubric_id).all()
    print('pos', len(positive_docs))

    temp_list = []
    for doc in positive_docs:
        temp_list.append(str(doc.doc_id))
    train_len = round(len(temp_list) * .8)
    for i in temp_list[:train_len]:
        new_set_train.append(i)
    for i in temp_list[train_len:]:
        new_set_test.append(i)

    train_set = TrainingSet(doc_ids=new_set_train, doc_num=len(new_set_train), name=rubric_name + '_train')
    test_set = TrainingSet(doc_ids=new_set_test, doc_num=len(new_set_test), name=rubric_name + '_test')
    session.add(train_set)
    session.add(test_set)
    session.commit()
    return train_set.set_id, test_set.set_id


def teach_and_test(rubric_id, tr_id, test_set, teach=False, verbose=False):
    if teach:
       teach_rubricator(tr_id, rubric_id, verbose=verbose)
       print('Обучение рубрикатора завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(tr_id, rubric_id, tr_set=tr_id, name='tr'))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, rubric_id, tr_set=tr_id, name='test'))


def polit_pressing():

    rubric_pp = rubrics['pp']
    rubric_ss = rubrics['ss']

    pp_train_set = sets['pp']['train_set']
    pp_test_set = sets['pp']['test_set']

    ss_train_set = sets['ss']['train_set']
    ss_test_set = sets['ss']['test_set']

    # training_set, test_set = create_sets_polit_press(rubric_pp,'politpressing')
    # print('Пллитпрессинг')
    # print(training_set, test_set)
    # training_set, test_set = create_sets_polit_press(rubric_ss,'svoboda sobrani')
    # print('Свобода собраний')
    # print(training_set, test_set)

    # set_id_pp = '9f3490b9-ea0c-462b-bf55-2e68f1e34161'
    # set_id_ss = '3b130596-e4a0-401c-ba6b-b09ec5385ba0'


    # set_id = db.get_set_id_by_name('politpressing_1')
    # print(set_id)
    # prepare_docs(set_id)
    # set_id = db.get_set_id_by_name('svoboda sobrani_1')
    # print(set_id)
    # prepare_docs(set_id)

    teach_and_test(rubric_pp, pp_train_set, ss_test_set, True)


def create_accepted_sets(session=None):
    if session is None:
        session = Driver.db_session()
    new_docs = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=72).all()
    print(len(new_docs))
    docs = dict()
    docs['neg'] = []
    neg_count = 0
    ans_count = 0
    for doc in new_docs:
        if len(doc.rubric_ids) == 0:
            docs['neg'].append(str(doc.doc_id))
            neg_count += 1
        for rubric_id in doc.rubric_ids:
            ans_count += 1
            new_ans = DocumentRubric(doc_id=str(doc.doc_id), rubric_id=str(rubric_id))
            # session.add(new_ans)
            if docs.get(str(rubric_id), None) is None:
                docs[str(rubric_id)] = []
            docs[str(rubric_id)].append(str(doc.doc_id))
    print('answers:', ans_count)
    print('Negative:', neg_count)
    set_ids = dict()
    print(docs.keys())
    for rubric_id in docs:
        print(len(docs[rubric_id]))
        rubric_key = ''
        for key in rubrics:
            if rubric_id in rubrics[key].values():
                rubric_key = key
                print(key, rubric_names[key])
        if not rubric_key == '':
            new_set = TrainingSet(doc_ids=docs[rubric_id],
                                  name='new_5_17'+rubric_names[rubric_key], doc_num=len(docs[rubric_id]))
            session.add(new_set)
            set_ids[rubric_key] = new_set
    session.commit()
    print('Neg:')
    print(docs['neg'])


def create_negative_sets(session=None):
    if session is None:
        session = Driver.db_session()
    negative_docs = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=71).all()
    print('neg', len(negative_docs))
    temp_list = []
    for doc in negative_docs:
        temp_list.append(str(doc.doc_id))
    len_train = round(len(temp_list) * .8)
    new_set = TrainingSet(doc_ids=temp_list[:len_train], name='train_negative', doc_num=len_train)
    session.add(new_set)
    new_set2 = TrainingSet(doc_ids=temp_list[len_train:], name='test_negative', doc_num=len(temp_list[len_train:]))
    session.add(new_set2)
    session.commit()
    print(new_set.set_id, len_train)
    print(new_set2.set_id, len(temp_list[len_train:]))


def create_new_sets(session=None):
    if session is None:
        session = Driver.db_session()
    ids = {}
    test_neg = db.get_set_docs(sets['negative']['test'])
    train_neg = db.get_set_docs(sets['negative']['train'])
    for key in range(1,7):
        tr_pos_set = db.get_set_docs(sets['1' + str(key)]['tr_pos_set'])
        test_pos_set = db.get_set_docs(sets['1' + str(key)]['test_pos_set'])

        temp_list = []
        for doc_id in tr_pos_set:
            temp_list.append(str(doc_id))
        for doc_id in train_neg[:2*len(temp_list)]:
            temp_list.append(str(doc_id))
        new_tr_set = TrainingSet(doc_ids=temp_list, name=rubric_names[str(key)] + '_train_2', doc_num=len(temp_list))

        temp_list = []
        for doc_id in test_pos_set:
            temp_list.append(str(doc_id))
        for doc_id in test_neg[:2 * len(temp_list)]:
            temp_list.append(str(doc_id))
        new_test_set = TrainingSet(doc_ids=temp_list, name=rubric_names[str(key)] + '_test_2', doc_num=len(temp_list))
        ids[str(key)] = [new_tr_set, new_test_set]
        session.add(new_tr_set)
        session.add(new_test_set)
    session.commit()
    for key in ids:
        print(key, rubric_names[key])
        print("'tr_set_2': '" + str(ids[key][0].set_id) + "',")
        print("'test_set_2': '" + str(ids[key][1].set_id) + "',")


def do_job():
    rubric_num = 'pp'
    version = ''
    set_num = version + rubric_num

    training_set = sets[set_num]['train_set_10']
    test_set = sets[set_num]['test_set_10']

    teach_and_test(rubrics[rubric_num]['pos'], training_set, test_set, True, verbose=True)


def test_2_models(model_id_1, model_id_2, test_set_id, rubric_id, protocol_file_name=""):

    """compute TP, FP, TN, FN, Precision, Recall and F-score on data from db"""
    result = {}
    # if protocol_file_name:
    #     result_docs = {'true_positive': [], 'false_positive': [], 'true_negative': [], 'false_negative': []}
    # right answers
    answers = db.get_rubric_answers(test_set_id, rubric_id)
    print('Количество правильных ответов: ', len(answers))

    # rubrication results
    rubrication_result_2 = db.get_rubrication_result(model_id_2, test_set_id, rubric_id)
    rubrication_result_1 = db.get_rubrication_result(model_id_1, test_set_id, rubric_id)

    print('Клличество ответов tf-idf', len(rubrication_result_1))
    print('Количество ответвв embedding', len(rubrication_result_2))
    print('Результаты рубрикатора на тестовой выборке')
    print('Fact        Tf-idf        Embeddings')
    for key in rubrication_result_2:
        key1 = answers[key]
        key2 = rubrication_result_1[key]
        key3 = rubrication_result_2[key]
        result_key = (key1, key2, key3)
        result[result_key] = result.get(result_key, 0) + 1

    for result_key in result:
        print(result_key[0], '          ',result_key[1], '          ', result_key[2], '          ', result[result_key])

    # if protocol_file_name:
    #     x = open(protocol_file_name, 'a', encoding='utf-8')
    #     x.write('ТЕКСТЫ ДОКУМЕНТОВ РАСРПДЕЛЕННЫЕ ПО ВАРИАНТАМ ОТВЕТА РУБРИКАТОРА:' + '\n')
    #     for result_key in result_docs:
    #         x.write('==========================================================' + '\n')
    #         x.write('==========================================================' + '\n')
    #         x.write(result_key + '\n')
    #         print_doc_texts_to_file(result_docs[result_key],x)
    #     x.close()


def compare_rubrication_result():
    rubric_num = '4'
    version = '2'
    set_num = version + rubric_num

    rubric_id = rubrics['pp']['pos']
    test_set = sets['pp']['test_set_2']
    # test_set = sets['1']['test_pn']
    embedding_id = 'ModelEP_0506_128_NonCons_6_3.pic'

    # На чем тренировали рубиику в последний раз
    training_set_id_for_rubric = db.get_set_id_by_rubric_id(rubric_id)
    # Буеем использовать модели, полученные на следующих учебных выборках
    training_set_id_tf_idf = training_set_id_for_rubric
    print('TF-IDF используем модель, обученную по выборке', training_set_id_tf_idf)
    training_set_id_embed = training_set_id_for_rubric
    # training_set_id_embed = sets['pp']['train_set_0']
    print('Embedding', training_set_id_embed)

    # Применение моделей, обученных на указанных выборках к тестовой выборке
    tf_idf_model_id = rb.spot_test_set_rubric(test_set, rubric_id, training_set_id=training_set_id_tf_idf)
    embedding_model_id = rb.spot_test_set_embedding_rubric(test_set, embedding_id, rubric_id, training_set_id=training_set_id_embed)

    test_2_models(tf_idf_model_id, embedding_model_id, test_set, rubric_id)


# compare_rubrication_result()
# do_job()