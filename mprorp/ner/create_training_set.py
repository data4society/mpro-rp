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
sets['2'] = {
    'tr_id_pn': 'b75dc32c-0b20-4dbc-af87-3bb2a24e5938', # pos + neg
    'tr_id_pnc': '5f128ce8-2c82-4ccd-a4a5-4b09c7c91ea5', # pos + neg + com
    'tr_id_pc': '908f2892-0b67-48c0-bc47-d128bfa0cd3f', # pos + com
    'tr_id_pc100': '829d2db3-3ec2-4c4a-b986-9e2e3deaaee1',
    'test_positive': 'c1293b5e-d1d4-4567-b6fa-c5a830c60d6a',
    'test_negative': 'ce6a4102-1f11-4811-a5c7-e2d8ef7c2231',
    'tr_pos': 'd23977ef-2dd2-46b2-84da-9b23b8ff71de',
    'tr_neg': 'f5989784-24f4-46e7-9b73-887c23bdd344',
    'test_pn': '63f12eb5-fa8b-4dff-b2d8-27ada121dcc0'
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
sets['5'] = {
    'tr_id_pn': '3bfb9d28-ee48-4021-857c-8d9e916a70d2', # pos + neg
    'tr_id_pnc': 'c4b9b04a-0686-4541-b247-8d2e8e28bdbc', # pos + neg + com
    'tr_id_pc': '7d02ca6c-fe4b-4a8c-abb4-e833529dedb4', # pos + com
    'tr_id_pc100': '27ecb9c4-9e7e-4805-b3dd-846a0512b848',
    'test_positive': 'e28daae0-f239-4bf1-a9af-8e4070d83f26',
    'test_negative': 'b7b645d0-c7d8-4c4c-8bed-9f7be061bcfe',
    'tr_pos': '98601bf3-84ce-47d3-8002-bb7355a23280',
    'tr_neg': '0382d97e-1806-4abd-8897-c143ba0f3a9b',
    'test_pn': '59090417-e05c-4151-99d0-9e8432a22288'
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
sets['04'] = {
    'tr_id_pn': 'e9a40771-88fd-4060-8a17-55c49f30925f', # pos + neg
    'tr_id_pnc': 'c9047cad-2784-4251-b55f-e4d3507b4d38', # pos + neg + com
    'tr_id_pc': 'e262d71b-bc9f-4de6-9841-c1719524a757', # pos + com
    'tr_id_pc100': 'ad425b5d-c22c-4502-8d4a-a62f4b12b8cc',
    'test_positive': '53d0f42a-9f48-4a54-9293-434ad108eacb',
    'test_negative': 'aeb689e7-a28c-4adf-a4ff-82ab343d761b',
    'tr_pos': '5969de73-831f-4714-9d86-50aded34ba18',
    'tr_neg': 'e4855bc6-c528-4bcc-8faf-e9e625856cff',
    'test_pn': '9574e5a5-9f6d-45a0-b50a-9680a8e2385f'
}
sets['06'] = {
    'tr_id_pn': 'f2a966a4-16a0-431b-84ab-6518137c94c2', # pos + neg
    'tr_id_pnc': 'd8566fd9-a2fa-4f5f-8e35-38703d0e6f4c', # pos + neg + com
    'tr_id_pc': '3873aeb3-f70f-440f-9037-af127dd4e00d', # pos + com
    'tr_id_pc100': '2ddca0d4-b514-4979-87fe-6d6826791cd6',
    'test_positive': '25eb5af9-8021-40ea-ab69-bd95adc6d752',
    'test_negative': 'd1e5dadb-f5bf-4cd5-9ce9-841bd1b71eb8',
    'tr_pos': '8c20da89-a46f-4b52-9411-e07f3c198bd2',
    'tr_neg': 'f35f33ca-c363-4f6f-a0fa-cad89345107c',
    'test_pn': '9f380071-151e-41ed-bcdb-5c8d69002970'
}
sets['11'] = {'new': 'ac9ea1cb-7b43-43ea-9a53-1ef968744299',
              'positive': 'b90e65c3-f862-4fb6-80b1-e6b8b3f126eb',
              'tr_pos_set': '9fa77db8-ef1e-43c0-9c00-a5379e0b05af',
              'test_pos_set': '4df1a71e-1e96-4031-a168-51df23979f15',
              'tr_set_2': '5bd69ab2-0c94-4f01-b77d-18013158f6ae',
              'test_set_2': '3ba807af-55a8-4732-aa8c-7df926b24243',
              'tr_set': '99b17109-40a9-4240-abdf-108a7df2605c',
              'test_set': '69086ef1-79b7-475f-b9c7-8e034bde04e5'}
sets['12'] = {'new': '10e44b91-9a3d-4f23-ad28-820a239a7a9e',
              'positive': 'edd6958b-6ec5-4fd3-b481-02a48679d00e',
              'tr_pos_set':   '6aed5a36-36c5-4da3-b7f0-0f38a9019861',
              'test_pos_set': '1155916c-b2c8-4c1d-a1d2-1f46ba1bb535',
              'tr_set_2': '9a11eb49-1c04-4017-98c7-c304851114ef',
              'test_set_2': '4cf38918-2b60-4c70-ac23-c7b2471a2515',
              'tr_set':       'b8e4d2dd-3270-47c7-bae6-288aefc16564',
              'test_set':     '2719c865-db49-49d2-8c1b-54730bccb7c5' }
sets['13'] = {'new': 'b3cd2c8e-24b5-4559-b64a-e1eb6cad7cad',
              'positive': 'bf1a3429-96a1-4209-bb0d-05d132e68351',
              'tr_pos_set': 'cd409090-16ca-49ac-a4a9-1a9f6f537f38',
              'test_pos_set': 'd78e518c-f5f1-4ef3-b3ca-f721eb3592e5',
              'tr_set_2': '83c44917-1328-43e9-ad93-030e9639f75c',
              'test_set_2': 'e94b1b8a-d27a-4136-a225-bba2e79e8d67',
              'tr_set': '66ee0f08-f3f6-42d6-a478-5224185feaa7',
              'test_set': '474eb9c0-1f0d-4a80-b610-bdf2f1a9623c'}
sets['14'] = {'new': 'dd262fc2-7d65-4c2f-b101-19216aae7ae9',
              'positive': '72c7a020-0874-4cb3-a223-ebc7ec20584b',
              'tr_pos_set': '2382885c-c3d2-46b8-9985-af8e51617365',
              'test_pos_set': '335706be-37f3-446c-8f11-442895dcb39a',
              'tr_set_2': '9e3881b3-f3db-42d1-adca-35d23a21646a',
              'test_set_2': 'c7b3a042-109b-4906-b5f0-6a9375fa732b',
              'tr_set': 'becd972f-e26b-4361-a049-58a54b8d67cc',
              'test_set': '34eb33b3-c593-4096-a965-42de8c60532f'}
sets['15'] = {'new': 'a3073be1-5470-4720-a379-8e20bf6fe505',
              'positive': '9fc9dcfd-cd8c-4e9f-8054-f038f536e64a',
              'tr_pos_set': '72ce51fb-41bd-40c8-9701-a3fcce0d711b',
              'test_pos_set': '5755fda2-4bee-4b6e-bdb3-5cd912eadc91',
              'tr_set_2': '56a63fa1-08da-4fe6-b503-720582a1c7f9',
              'test_set_2': '6cec9beb-ab1c-454d-b03d-42134587b743',
              'tr_set': '7f0c0a6d-ddf0-48b4-88bf-06846ff87f2d',
              'test_set': '5d2abf1c-b9f4-4362-a8a6-60fd0ec5c82f'}
sets['16'] = {'new':          '8e90e65a-25e4-493b-beda-3bb920c230d1',
              'positive':     '6a1ea451-6bf9-4529-a816-75fae78569c2',
              'tr_pos_set':   'ff27a310-226b-41d3-acfc-d9b7e9069148',
              'test_pos_set': '9f6d0dbc-804f-46f5-87a3-dcefb167af80',
              'tr_set_2': '9038069d-f579-46bd-9ace-7e1e226ea609',
              'test_set_2': '6e481c09-36a9-4ca7-a8cc-fb42c7e72098',
              'tr_set':       '70e6ec17-2a60-41b0-adcd-e8360cdc0792',
              'test_set':     '8ae5bd11-77ce-4718-9045-8e0967460260'}
sets['negative'] = {'all':   '779bd1d0-887c-4c81-bfc5-8b4632f9b81e',
                    'train': '2009195a-2c4a-4120-88ac-147464a9ccb5',
                    'test':  '2b4be3c1-b217-4e3e-a4a7-8ab3fc767d7d'}



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


def teach_and_test(rubric_id, tr_id, test_set, teach=False):
    if teach:
       teach_rubricator(tr_id, rubric_id)
       print('Обучение рубрикатора завершено')

    print('Результаты рубрикатора на учебной выборке')
    print(test_model(tr_id, rubric_id, tr_set=tr_id, name='tr'))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, rubric_id, tr_set=tr_id, name='test'))


def polit_pressing():

    rubric_pp = '14e511c0-2ce9-49b2-9d0c-f16c383765d1'
    rubric_ss = 'db9baa28-e201-47a6-aada-14f44f42e98f'

    pp_train_set = '0364c8e3-ebcd-4fa2-b14a-3f10c498bcd3'
    pp_test_set = 'dca01625-d655-4900-9b32-6a548c7dc0dd'

    ss_train_set = '69565f15-73ea-4d06-84aa-d3e5cea57ee7'
    ss_test_set = '498aac37-efd8-4b9c-932a-17d6291a2ab6'

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



# for key in range(1,7):
#     print('---------------------------------------------------------------------------------------------------------------------')
#     print(key)
#     prepare_docs(sets['1' + str(key)]['new'])

# exit()

# common
# tr_com = '265fac6f-4b3e-466d-b7fe-fcdc90978a4e'
# tr_com100 = 'c0b20817-e5f2-4fcb-bd39-ef1f53b403a3'
# test_com = '5544e81e-6dda-458f-9f79-e40d990e6e94'

# give_name_to_sets()

# conf = [{'rubric_id': rubrics['4']['pos'], 'rubric_minus_id': rubrics['4']['neg'], 'set_name': 'lgbt_tr_id_pc'},
#         {'rubric_id': rubrics['6']['pos'], 'rubric_minus_id': rubrics['6']['neg'], 'set_name': 'internet_tr_id_pn'}]
#
# doc_id = 'f98e75ea-feee-480d-80cc-fe5b4a21e727'
# rb.spot_doc_rubrics2(doc_id, conf, verbose=True)

rubric_num = '4'
version = '1'
set_num = version + rubric_num

# tr_id_pn = sets[set_num]['tr_id_pn']  # pos + neg
# tr_id_pnc = sets[set_num]['tr_id_pnc'] # pos + neg + com
# tr_id_pc = sets[set_num]['tr_id_pc']
# tr_id_pc100 = sets[set_num]['tr_id_pc100']
# test_positive = sets[set_num]['test_positive']
# test_negative = sets[set_num]['test_negative']
# test_pn = sets[set_num]['test_pn']
# tr_pos = sets[set_num]['tr_pos']
# tr_neg = sets[set_num]['tr_neg']

# training_set = tr_id_pnc
training_set = sets[set_num]['tr_set_2']
test_set = sets[set_num]['test_set_2']

teach_and_test(rubrics[rubric_num]['pos'], training_set, test_set, True)


