import unittest

from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.tomita.tomita_run import run_tomita
import mprorp.analyzer.rubricator as rb
import mprorp.ner.feature as ner_feature
import mprorp.analyzer.db as db
from mprorp.tomita.grammars.config import config


class SimpleTomitaTest(unittest.TestCase):

    def test_tomita_person(self):
        dropall_and_create()
        # my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.', type='article')
        my_doc = Document(stripped=mytext, type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc(doc_id)
        for gram in config:
            run_tomita(gram, str(doc_id))
        ner_feature.create_tomita_feature(str(doc_id), config.keys())

        ner_feature.create_tomita_feature(doc_id, config.keys())
        gaz_id = db.put_gazetteer('gaz1', ['площадь', 'улица', 'переулок'])
        ner_feature.create_gazetteer_feature(doc_id, gaz_id)
        print(db.get_ner_feature(doc_id))


    def test_embedding_feature(self):
        dropall_and_create()
        my_doc = Document(
            stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.',
            type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc(doc_id)
        ner_feature.create_embedding_feature(doc_id)
        features = db.get_ner_feature(doc_id)
        # print(features)
        self.assertEqual(features[(0, 13, 'embedding')], {'который_APRO': 1})
        self.assertEqual(features[(0, 12, 'embedding')], {',': 1})

    def test_morpho_feature(self):
        dropall_and_create()
        my_doc = Document(
            stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.',
            type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc(doc_id)
        ner_feature.create_morpho_feature(doc_id)
        features = db.get_ner_feature(doc_id)
        print(features[(0, 11, 'morpho')])
        print(len(features[(0, 11, 'morpho')]))
        # self.assertEqual(features[(0, 11, 'embedding')], {'который_APRO': 1})

mytext = '''Следственный судья Киевского райсуда Харькова Валентина Божко удовлетворила ходатайство прокуратуры об аресте бывшего народного депутата от Компартии Украины Аллы Александровской, подозреваемой в сепаратизме, посягательстве на территориальную целостность Украины и попытке подкупа депутатов.
"По решению суда подозреваемой в посягательстве на территориальную целостность и неприкосновенность, а также даче неправомерной выгоды служебному лицу, избрана мера пресечения в виде содержания под стражей на 2 месяца без определения суммы залога", - сообщила пресс-служба прокуратуры Харьковской области.
В свою очередь адвокат А.Александровской Александр Шадрин заявил, что считает избранную меру пресечения необоснованной.
"Это необоснованно. Конечно, мы будем подавать апелляцию", - сказал А.Шадрин корреспонденту агентства "Интерфакс-Украина".
Как сообщалось, 28 июня адвокат А.Александровской А.Шадрин сообщил, что у его подзащитной прошел обыск и она была задержана. Ей инкриминируют ч.2 ст.110 (посягательство на территориальную целостность и неприкосновенность Украины) и ч.3 ст.369 (предложение, обещание или предоставление неправомерной выгоды служебному лицу) Уголовного кодекса Украины.
29 июня в СБУ подтвердили, что правоохранители задержали А.Александровскую, решается вопрос о ее аресте, а ее сын Александр, который скрывается в РФ, извещен о подозрении и объявлен в розыск.
А.Александровская с 1996 года была бессменным первым секретарем Харьковского обкома КПУ, дважды избиралась депутатом Харьковского облсовета, четырежды – народным депутатом Украины. В 2008 году стала Почетным гражданином Харькова.'''