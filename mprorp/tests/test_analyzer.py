import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import mprorp.analyzer.rubricator as rb
import mprorp.analyzer.db as db


class SimpleDBTest(unittest.TestCase):

    def test_stop_lemmas(self):
        self.assertEqual(len(rb.stop_lemmas) > 100, True)
        self.assertEqual('ранее' in rb.stop_lemmas, True)

    def test_morpho(self):
        # morpho analysis
        dropall_and_create()
        # doc_stripped = 'Эти типы стали есть, на складе. Проголодались! Вот так. "Кладовка" "-" крупнейший складской комплекс'
        doc_stripped = mytext2
        my_doc = Document(stripped=doc_stripped, type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc2(doc_id)
        morpho = db.get_morpho(doc_id)
        print(morpho)
        doc_text = ''
        for element in morpho:
            if rb.is_sentence_end(element) == False:
                doc_text = doc_text + element.get('text', '')
        self.assertEqual(doc_text.replace('\n',''), doc_stripped.replace('\n',''))

    def test_lemmas_freq(self):
        # morpho analysis
        dropall_and_create()
        my_doc = Document(stripped='Эти типы стали есть на складе', type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc2(doc_id)
        rb.lemmas_freq_doc2(doc_id)
        lemmas = db.get_lemmas(doc_id)
        self.assertEqual(lemmas['склад'], 1)

    def test_training_set_idf(self):
        set_id, rubric_id = fill_db()
        rb.idf_object_features_set(set_id)
        # check we can overwrite idf:
        rb.idf_object_features_set(set_id)
        result = select(ObjectFeatures.doc_id, ObjectFeatures.set_id == set_id).fetchall()
        self.assertEqual(len(result), 10)

    def test_model(self):
        set_id, rubric_id = fill_db()
        rb.idf_object_features_set(set_id)
        rb.learning_rubric_model(set_id, rubric_id)
        model = db.get_model(rubric_id, set_id)
        self.assertEqual(model['features_num'], 11)

    def test_rubricator(self):
        set_id, rubric_id = fill_db()

        rb.idf_object_features_set(set_id)
        rb.learning_rubric_model(set_id, rubric_id)

        for doc_id in db.get_set_docs(set_id):
            rb.spot_doc_rubrics2(doc_id, {rubric_id: None})
            # check we can overwrite rubrication results:
            rb.spot_doc_rubrics2(doc_id, {rubric_id: None})

        model_id = db.get_model(rubric_id, set_id)["model_id"]

        result = rb.f1_score(model_id, set_id, rubric_id)
        self.assertEqual(result['f1'], 1)

        # another way to spot rubrics
        rb.spot_test_set_rubric(set_id, rubric_id)
        result = rb.f1_score(model_id, set_id, rubric_id)
        self.assertEqual(result['f1'], 1)


def fill_db():

    docs = ["Письмо Маши Васе",
            "First документ Пети",  # check processing english word
            "Первое письмо Маши",
            "Второй документ Маши",
            "Первый документ Васи",
            "222 документ Пети",  # check processing numbers
            "Первое письмо Пети",
            "Первое письмо Васи",
            "Первый документ Маши",
            "Письмо Маши Пете"]
    answers = [1, 0, 1, 0, 0, 0, 1, 1, 0, 1]

    tr_set = []

    for doc in docs:
        doc_db = Document(stripped=doc, type='article')
        insert(doc_db)
        tr_set.append(doc_db.doc_id)

    new_rubric = Rubric(name="Маша")
    insert(new_rubric)
    rubric_id = str(new_rubric.rubric_id)

    for i in range(10):
        if answers[i]:
            insert(DocumentRubric(doc_id=str(tr_set[i]), rubric_id=rubric_id))

    for doc_id in tr_set:
        rb.morpho_doc2(str(doc_id))
        rb.lemmas_freq_doc2(str(doc_id))

    set_id = str(db.put_training_set(tr_set))

    return set_id, rubric_id

mytext = '''Следственный судья Киевского райсуда Харькова Валентина Божко удовлетворила ходатайство прокуратуры об аресте бывшего народного депутата от Компартии Украины Аллы Александровской, подозреваемой в сепаратизме, посягательстве на территориальную целостность Украины и попытке подкупа депутатов.
"По решению суда подозреваемой в посягательстве на территориальную целостность и неприкосновенность, а также даче неправомерной выгоды служебному лицу, избрана мера пресечения в виде содержания под стражей на 2 месяца без определения суммы залога", - сообщила пресс-служба прокуратуры Харьковской области.
В свою очередь адвокат А.Александровской Александр Шадрин заявил, что считает избранную меру пресечения необоснованной.
"Это необоснованно. Конечно, мы будем подавать апелляцию", - сказал А.Шадрин корреспонденту агентства "Интерфакс-Украина".
Как сообщалось, 28 июня адвокат А.Александровской А.Шадрин сообщил, что у его подзащитной прошел обыск и она была задержана. Ей инкриминируют ч.2 ст.110 (посягательство на территориальную целостность и неприкосновенность Украины) и ч.3 ст.369 (предложение, обещание или предоставление неправомерной выгоды служебному лицу) Уголовного кодекса Украины.
29 июня в СБУ подтвердили, что правоохранители задержали А.Александровскую, решается вопрос о ее аресте, а ее сын Александр, который скрывается в РФ, извещен о подозрении и объявлен в розыск.
А.Александровская с 1996 года была бессменным первым секретарем Харьковского обкома КПУ, дважды избиралась депутатом Харьковского облсовета, четырежды – народным депутатом Украины. В 2008 году стала Почетным гражданином Харькова.'''

mytext2 = '''
1. Арнольд Лобел — серия книг о Кваке и Жабе («Розовый жираф»).
2. Евгений и Николай Чарушины — рассказы («Акварель»).'''

