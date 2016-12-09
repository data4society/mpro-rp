import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
import random

rubric_no_name = '35ed00df-3be5-4533-9f13-7535a95dba62'
rubrics = {
    '1': {'pos': '10180591-8d58-4d6e-a3dd-cc7df1cbb671',
          'neg': 'ec434320-3a42-4bbc-aa2f-fb95dc28e9db'},# искусство
    '2': {'pos': '264468df-6c20-4a66-8f4f-07c91f200e37',
          'neg': '49596f63-353a-4207-a076-4ca0bd66eca3'},# отчисление и увольнение
    '3': {'pos': '8676d718-7ca7-49a4-a815-8bc2efd9ee2e',
          'neg': 'd4a52335-34f7-4677-a20b-21b39983088a'},# насилие
    '4': {'pos': 'c1486c39-62f5-4476-aca0-6641af0ba11d',
          'neg': '4c5882dc-0dd1-4382-813b-18fb02650e02'},# ЛГБТ
    '5': {'pos': 'd9b9f38e-77e0-4ab5-8a58-98e8ff5e6d21',
          'neg': '6aac7df6-98a5-42e1-a463-4c7f222269a8'},# угрозы
    '6': {'pos': 'f079f081-d1ab-4136-ba4f-520ac59b70b8',
          'neg': 'a283ced3-32b5-4ae4-a9a6-440107c3e9e2'},# интернет
}
rubric_names = {
    '1': 'iskustvo',
    '2': 'uvolnenie',
    '3': 'nasilie',
    '4': 'lgbt',
    '5': 'ugrozy',
    '6': 'internet'
}

sets = dict()
sets['1'] = {
    'tr_id_pn': '1f413604-d6a7-4acb-a060-77cf6a6ddd19', # pos + neg
    'tr_id_pnc': '858a0631-42b5-40d4-b446-e457ea1d4ff7', # pos + neg + com
    'tr_id_pc': 'a0596a43-99fa-411e-a447-1cfc07a36b53', # pos + com
    'tr_id_pc100': '7111ef46-9f8d-4ca4-a9c9-50a837d39116',
    'test_positive': '77aa00f2-81b7-40d5-8bac-c9d7755d2b2e',
    'test_negative': '377cdb8c-ccf0-4f2f-8fe6-17289709b0b1',
    'tr_pos': '042b0854-b213-4987-8568-11ddde77d461',
    'tr_neg': '47fe435c-f7c9-4a5c-9379-71b33c29a06a',
    'test_pn': 'a467dd1d-8028-4446-b9d7-203b773b375c'
}
sets['3'] = {
    'tr_id_pn': 'c5498c2f-b11a-4094-97fb-6e002f6c3a52', # pos + neg
    'tr_id_pnc': 'bfc3d5ab-0d1c-4531-b333-84712b0c0113', # pos + neg + com
    'tr_id_pc': '90898161-57dc-4ce7-8239-ef3a7b1cd2d1', # pos + com
    'tr_id_pc100': '06c530b3-a8e9-4d08-9883-128689996f7b',
    'test_positive': '848408ce-b69d-4d6d-8360-795f183303a0',
    'test_negative': 'f1dc071f-6c71-4a18-bc10-0273f1b69952',
    'tr_pos': '916f13a2-4d43-4bdc-ba52-ed9feadfe387',
    'tr_neg': '105ca410-7d84-4eff-9e45-9b8c29507bb6',
    'test_pn': 'a65e5faf-c46e-485b-bc5b-1c8ebe54efeb'
}
sets['4'] = {
    'tr_id_pn': 'c020af3c-1e0e-403f-8ffc-8ff2c974c907', # pos + neg
    'tr_id_pnc': '19bb2c5f-a609-44da-b96e-448918d08d19', # pos + neg + com
    'tr_id_pc': '83fdb43a-7a31-4831-b675-ca2f6439df13', # pos + com
    'tr_id_pc100': 'c020af3c-1e0e-403f-8ffc-8ff2c974c907',
    'test_positive': '45f2309c-096f-47bc-b19c-fff7b58a2de5',
    'test_negative': '5f8e26d9-0067-4d18-be6b-36ccd8a8df74',
    'tr_pos': '6e98a44d-66f1-4d7f-adaa-83a77126b748',
    'tr_neg': '23d197c3-467e-49d8-8a07-5336ec2b18fe',
    'test_pn': 'a5a0f8db-ae75-4055-a080-e93ac6c81b39'
}
sets['6'] = {
    'tr_id_pn': '09b95033-6fe8-4df9-89e5-9472cbd2f573',
    'tr_id_pnc': 'c5b4dc5b-04a5-4255-807c-655f6817bdee',
    'tr_id_pc': 'd2b6d3ec-b533-4702-8afd-c3365141119e',
    'tr_id_pc100': 'e44f56ac-893a-4d2c-97e8-2746ab758517',
    'test_positive': 'c2f7f817-6fed-4b0a-9a3e-014614405e7e',
    'test_negative': '70bc5194-2073-4c0a-a783-86ffb4fa9fd4',
    'tr_pos': '9939f387-d3aa-4a9c-be37-064bf844db2d',
    'tr_neg': '3e936aff-a728-4b63-90f4-3f516d02560f',
    'test_pn': '0706a451-d995-41d4-af9b-e8e0451ca465'
}



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
    rb.idf_object_features_set(set_id)
    rb.learning_rubric_model(set_id, rubric_id, verbose=verbose)
    # rb.learning_rubric_model_coeffs(set_id, doc_coefficients, rubric_id, savefiles=False, verbose=verbose)


def test_model(set_id, rubric_id, tr_set=None, name=''):
    model_id = rb.spot_test_set_rubric(set_id, rubric_id, training_set_id=tr_set)
    print('При тестировании для рубрики ', rubric_id, ' использована модель ', model_id)
    # for doc_id in db.get_set_docs(set_id):
    #     rb.spot_doc_rubrics2(doc_id, {rubric_id: None}, verbose=True)
    model_id = db.get_model(rubric_id)["model_id"]
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


def create_sets(rubric_id):
    session = Driver.db_session()
    doc_ids_pos = db.get_moderated_docs(rubric_id)
    add_rubric_to_docs(rubric_id, doc_ids_pos)
    random.shuffle(doc_ids_pos)
    set_pos_dev = db.put_training_set(doc_ids_pos[:10])
    set_pos_train = db.put_training_set(doc_ids_pos[10:])
    session.commit()
    return set_pos_train, set_pos_dev, doc_ids_pos[10:]


def give_name_to_sets(rub_num):
    session = Driver.db_session()
    for set_name in sets[rub_num]:
        Tr_set = session.query(TrainingSet).filter(TrainingSet.set_id == sets[rub_num][set_name]).one()
        Tr_set.name = rubric_names[rub_num] + '_' + set_name
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


# common
tr_com = '265fac6f-4b3e-466d-b7fe-fcdc90978a4e'
tr_com100 = 'c0b20817-e5f2-4fcb-bd39-ef1f53b403a3'
test_com = '5544e81e-6dda-458f-9f79-e40d990e6e94'

# give_name_to_sets()

# conf = [{'rubric_id': rubrics['4']['pos'], 'rubric_minus_id': rubrics['4']['neg'], 'set_name': 'lgbt_tr_id_pc'},
#         {'rubric_id': rubrics['6']['pos'], 'rubric_minus_id': rubrics['6']['neg'], 'set_name': 'internet_tr_id_pn'}]
#
# doc_id = 'f98e75ea-feee-480d-80cc-fe5b4a21e727'
# rb.spot_doc_rubrics2(doc_id, conf, verbose=True)

rubric_num = '3'

give_name_to_sets(rubric_num)
exit()

# set_train, set_dev, docs_train_pos = create_sets(rubrics[rubric_num]['pos'], )
# print(rubric_names[rubric_num], 'positive', set_train, set_dev)
# prepare_docs(set_dev)
#
# set_train, set_dev, docs_train_neg = create_sets(rubrics[rubric_num]['neg'])
# print(rubric_names[rubric_num], 'negative', set_train, set_dev)
# prepare_docs(set_dev)

# docs_c100 = list(db.get_set_docs(tr_com))
# random.shuffle(docs_c100)
# set_c100 = db.put_training_set(docs_c100[:100])
# print('set_c100', set_c100)



tr_id_pn = sets[rubric_num]['tr_id_pn']  # pos + neg
tr_id_pnc = sets[rubric_num]['tr_id_pnc'] # pos + neg + com
tr_id_pc = sets[rubric_num]['tr_id_pc']
tr_id_pc100 = sets[rubric_num]['tr_id_pc100']
test_positive = sets[rubric_num]['test_positive']
test_negative = sets[rubric_num]['test_negative']
test_pn = sets[rubric_num]['test_pn']
tr_pos = sets[rubric_num]['tr_pos']
tr_neg = sets[rubric_num]['tr_neg']

docs_train = list(db.get_set_docs(tr_pos))
docs_train.extend(list(db.get_set_docs(tr_com100)))
# docs_train.extend(list(db.get_set_docs(tr_neg)))
new_set = db.put_training_set(docs_train)
print('new_set...', new_set)
exit()

# Восстановление рубрик документов
# add_rubric_to_docs(rubrics[rubric_num]['pos'], db.get_set_docs(test_positive))
# add_rubric_to_docs(rubrics[rubric_num]['pos'], db.get_set_docs(tr_pos))

training_set = tr_id_pc
# prepare_docs(tr_pos)
# prepare_docs(tr_neg)
teach_rubricator(training_set, rubrics[rubric_num]['pos'])
# print('Обучение рубрикатора завершено')

print('Результаты рубрикатора на учебной выборке pn')
print(test_model(tr_id_pn, rubrics[rubric_num]['pos'], tr_set=training_set, name='tr'))
print('Результаты рубрикатора на учебной выборке com')
print(test_model(tr_com, rubrics[rubric_num]['pos'], tr_set=training_set, name='tr'))
print('Результаты рубрикатора на тестовой общеотрицательной выборке')
print(test_model(test_com, rubrics[rubric_num]['pos'], tr_set=training_set, name='tr'))
print('Результаты рубрикатора на тестовой выборке')
print(test_model(test_pn, rubrics[rubric_num]['pos'], tr_set=training_set, name='test'))



