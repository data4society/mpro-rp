import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
import random
from mprorp.ner.set_list import sets, rubrics, rubric_names
from mprorp.config.settings import learning_parameters as lp
from mprorp.ner.paragraph_embedding import teach_and_test as par_emb_teach_and_test
from mprorp.ner.paragraph_embedding import filename as embedding_id


def create_sets():
    all_positive = sets['pp']['positive']
    all_negative = sets['negative']['all2']
    test_set = sets['pp']['test_set_2']

    all_positive_docs = db.get_set_docs(all_positive)
    all_negative_docs = db.get_set_docs(all_negative)
    len_positive = len(all_positive_docs)
    len_negative = len(all_negative_docs)
    test_docs = db.get_set_docs(test_set)
    train_set_docs = []
    while len(train_set_docs) < 50:
        index = random.randrange(len_positive)
        if not (all_positive_docs[index] in test_docs):
            train_set_docs.append(all_positive_docs[index])
    while len(train_set_docs) < 150:
        index = random.randrange(len_negative)
        if not (all_negative_docs[index] in test_docs):
            train_set_docs.append(all_negative_docs[index])
    session = Driver.db_session()
    new_tr_set = TrainingSet(doc_ids=train_set_docs, doc_num=len(train_set_docs), name='Active Learning set 1')
    session.add(new_tr_set)
    session.commit()
    print(new_tr_set.set_id)

    while len(train_set_docs) < 200:
        index = random.randrange(len_positive)
        if not ((all_positive_docs[index] in test_docs) or (all_positive_docs[index] in train_set_docs)):
            train_set_docs.append(all_positive_docs[index])
    while len(train_set_docs) < 300:
        index = random.randrange(len_negative)
        if not ((all_negative_docs[index] in test_docs) or (all_negative_docs[index] in train_set_docs)):
            train_set_docs.append(all_negative_docs[index])
    session = Driver.db_session()
    new_tr_set = TrainingSet(doc_ids=train_set_docs, doc_num=len(train_set_docs), name='Active Learning set 2')
    session.add(new_tr_set)
    session.commit()
    print(new_tr_set.set_id)


def teach_rubricator(set_id, rubric_id, calc_idf=False, verbose=False):
    if calc_idf:
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


def quick_start():
    rubric_id = rubrics['pp']['pos']
    all_positive = sets['pp']['positive']
    all_negative = sets['negative']['all2']
    test_set = sets['pp']['test_set_2']

    quick_start_1 = sets['pp']['quick_start_1']
    quick_start_2 = sets['pp']['quick_start_2']

    teach_rubricator(quick_start_1, rubric_id, calc_idf=False, verbose=True)
    print('Обучение рубрикатора на 1й выборке завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(quick_start_1, rubric_id, tr_set=quick_start_1))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, rubric_id, tr_set=quick_start_1))

    teach_rubricator(quick_start_2, rubric_id, calc_idf=False, verbose=True)
    print('Обучение рубрикатора на 2й выборке завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(quick_start_2, rubric_id, tr_set=quick_start_2))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, rubric_id, tr_set=quick_start_2))

    model = db.get_model(rubric_id, quick_start_1)

    probability = db.get_rubrication_probability(model['model_id'], test_set, rubric_id)
    positive_list = []
    negative_list = []
    quick_start_1_docs = list(db.get_set_docs(quick_start_1))
    for doc_id in probability:
        if doc_id in quick_start_1_docs:
            continue
        if probability[doc_id] > .5:
            positive_list.append(probability[doc_id])
        else:
            negative_list.append(-probability[doc_id])
    positive_list.sort()
    negative_list.sort()
    min_prob = -negative_list[100]
    max_prob = positive_list[50]
    new_docs = []
    for doc_id in probability:
        if (probability[doc_id] > min_prob) and (probability[doc_id] < max_prob) and not (doc_id in quick_start_1_docs):
            new_docs.append(doc_id)
    quick_start_1_docs.extend(new_docs)

    print(len(quick_start_1_docs))
    print(min_prob, max_prob)
    # session = Driver.db_session()
    # quick_start_3 = TrainingSet(doc_ids=quick_start_1_docs, doc_num=len(quick_start_1_docs), name='Active Learning set 3')
    # session.add(quick_start_3)
    # session.commit()
    # print(quick_start_3.set_id)
    quick_start_3 = '31a4ce43-d7e0-4646-93d7-cc27195349c6'

    teach_rubricator(quick_start_3, rubric_id, calc_idf=True, verbose=True)
    print('Обучение рубрикатора на 2й выборке завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(quick_start_3, rubric_id, tr_set=quick_start_3))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, rubric_id, tr_set=quick_start_3))


def quick_start2():
    rubric_id = rubrics['pp']['pos']
    all_positive = sets['pp']['positive']
    all_negative = sets['negative']['all2']
    test_set = sets['pp']['test_set_2']

    quick_start_1 = sets['pp']['quick_start_1']
    quick_start_2 = sets['pp']['quick_start_2']

    quick_start_3 = '31a4ce43-d7e0-4646-93d7-cc27195349c6'

    teach_rubricator(quick_start_3, rubric_id, calc_idf=True, verbose=True)
    print('Обучение рубрикатора на 2й выборке завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(quick_start_3, rubric_id, tr_set=quick_start_3))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, rubric_id, tr_set=quick_start_3))


def quick_start_pe():
    rubric_id = rubrics['pp']['pos']
    test_set = sets['pp']['test_set_2']

    quick_start_1 = sets['pp']['quick_start_1']
    quick_start_2 = sets['pp']['quick_start_2']

    par_emb_teach_and_test(quick_start_1, test_set, rubric_id)
    par_emb_teach_and_test(quick_start_2, test_set, rubric_id)

    # model = db.get_model(rubric_id, quick_start_1)
    model = db.get_model_embedding(rubric_id, embedding_id, quick_start_1)

    probability = db.get_rubrication_probability(model['model_id'], test_set, rubric_id)
    positive_list = []
    negative_list = []
    quick_start_1_docs = list(db.get_set_docs(quick_start_1))
    for doc_id in probability:
        if doc_id in quick_start_1_docs:
            continue
        if probability[doc_id] > .5:
            positive_list.append(probability[doc_id])
        else:
            negative_list.append(-probability[doc_id])
    positive_list.sort()
    negative_list.sort()
    min_prob = -negative_list[100]
    max_prob = positive_list[50]
    new_docs = []
    for doc_id in probability:
        if (probability[doc_id] > min_prob) and (probability[doc_id] < max_prob) and not (doc_id in quick_start_1_docs):
            new_docs.append(doc_id)
    quick_start_1_docs.extend(new_docs)

    print(len(quick_start_1_docs))
    print(min_prob, max_prob)
    session = Driver.db_session()
    quick_start_3_set = TrainingSet(doc_ids=quick_start_1_docs, doc_num=len(quick_start_1_docs), name='Active Learning set 3')
    session.add(quick_start_3_set)
    session.commit()
    print(quick_start_3_set.set_id)
    # quick_start_3 = '31a4ce43-d7e0-4646-93d7-cc27195349c6'
    quick_start_3 = str(quick_start_3_set.set_id)

    teach_rubricator(quick_start_3, rubric_id, calc_idf=True, verbose=True)
    print('Обучение рубрикатора на 2й выборке завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(quick_start_3, rubric_id, tr_set=quick_start_3))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, rubric_id, tr_set=quick_start_3))



# quick_start_pe()

