import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb

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


def add_rubric_to_doc(rubric_id, session=None):
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


def teach_rubricator(set_id, rubric_id, session=None):
    if session is None:
        session = Driver.db_session()
    docs = session.query(TrainingSet.doc_ids).filter_by(set_id=set_id)[0][0]
    n = len(docs)
    for doc_id in docs:
        # print(str(n) + ' docs left')
        rb.morpho_doc2(str(doc_id))
        rb.lemmas_freq_doc2(str(doc_id))
        n -= 1
    rb.idf_object_features_set(set_id)
    rb.learning_rubric_model(set_id, rubric_id)


def test_model(set_id, rubric_id):
    model_id = rb.spot_test_set_rubric(set_id, rubric_id)
    print('При тестировании для рубрики ', rubric_id, ' использована модель ', model_id)
    # for doc_id in db.get_set_docs(set_id):
    #     rb.spot_doc_rubrics2(doc_id, {rubric_id: None})
    # model_id = db.get_model(rubric_id)["model_id"]

    result = rb.f1_score(model_id, set_id, rubric_id)
    return result


def prepare_docs(set_id):
    for doc_id in db.get_set_docs(set_id):
        rb.morpho_doc2(doc_id)
        rb.lemmas_freq_doc2(doc_id)


def do_exercise(rubric_id):

    # add_rubric_to_doc(rubric_id)
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
    teach_rubricator(tr_id, rubric_id)
    print('Обучение рубрикатора завершено')
    print('Результаты рубрикатора на учебной выборке')
    print(test_model(tr_id, rubric_id))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_id, rubric_id))

rubric_1 = '19848dd0-436a-11e6-beb8-9e71128cae21'
rubric_2 = '19848dd0-436a-11e6-beb8-9e71128cae02'

sets = {rubric_1: {'train': 'bcc7f879-8745-459f-8cda-963ae51fa878',
                   'test':  'c8e1dbac-6a30-47f6-8a64-e383c748d559'},
        rubric_2: {'train': '17620f74-bf7a-4467-b6cc-e11b8acd727d',
                   'test':  'c3fabc6e-68c7-4a01-8ead-363dfab7b7e6'}}
#  sets = {rubric_1: {'train': 'ced81603-5621-4391-9c5d-02044075cab8',
#                    'test':  'e51e4995-5c4f-48be-a23a-8b58f6854e2f'},
#         rubric_2: {'train': '5f76733a-e1f6-4ae4-8662-2915455cef53',
#                    'test':  '869df84f-8435-483b-87a0-9043f8703108'}}

# sets = {rubric_1: None,
#         rubric_2: None}


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
print('ассоциации')
do_exercise(rubric_1) #свобода ассоциаций
print('собрания')
do_exercise(rubric_2) #свобода собраний


doc_id = '1252213c-e609-4e7d-b55d-85f3b2a2421e'
# doc_id = '4057e7d3-aa54-48b5-9b53-23a374c8cb40'
doc_id = '6fc81073-f43c-412a-a466-1456a007897b'
doc_id = '2a8ccd39-bd5d-4450-a653-1f90098fb810'
doc_id = '7d70cb95-a8c4-4a69-8335-19d8ed6c4b50'
doc_id = '0d28c395-616a-4a42-94ab-2951493f4392'
doc_id = '958c4a1b-544f-46d0-8e66-59d825dd1ca2'
# doc_id = 'd6cd6d75-fddd-45f9-80e4-db7ff6812a06'
doc_id = '012d0899-a066-4daa-9b34-ee8d3b6e91dd'
doc_id = '7e2904bf-ef62-4bab-b67f-338aa4c8906a'
# rb.morpho_doc2(doc_id)
# rb.lemmas_freq_doc2(doc_id)

# session = Driver.db_session()
# doc = session.query(Document).filter_by(doc_id=doc_id).first()
# print(doc.stripped)
# print(doc.morpho)
# rubrics = {rubric_1: 'ced81603-5621-4391-9c5d-02044075cab8', rubric_2: '5f76733a-e1f6-4ae4-8662-2915455cef53'}
# rb.spot_doc_rubrics(doc, rubrics, session=session, verbose=True)
# print(doc.rubric_ids)
# session.commit()

#1 Создание обучающей выборки
#print(len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[0]), len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[1])) #свобода ассоциаций
#print(len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[0]), len(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[1])) #свобода собраний
#2 Запись в таблицу DocumentRubrics
#add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[0], '19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций
#print('Done')
#add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[0], '19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний
#print('Done')
#add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae21')[1], '19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций
#print('Done')
#add_rubric_to_doc(create_training_set('19848dd0-436a-11e6-beb8-9e71128cae02')[1], '19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний
#print('Done')
#3 Запись в таблицу TrainingSet
#write_training_set('19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций train
#write_training_set('19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний train
#write_test_set('19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций test
#write_test_set('19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний test
#4 Обучение и Тест
#teach_rubricator(tr_set_id, '19848dd0-436a-11e6-beb8-9e71128cae21') #свобода ассоциаций
#print('Done')
#print(test_model(test_set_id, '19848dd0-436a-11e6-beb8-9e71128cae21')) #свобода ассоциаций
#teach_rubricator(tr_set_id, '19848dd0-436a-11e6-beb8-9e71128cae02') #свобода собраний
#print('Done')
#print(test_model(test_set_id, '19848dd0-436a-11e6-beb8-9e71128cae02')) #свобода собраний

