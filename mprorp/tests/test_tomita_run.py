import unittest

from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.tomita.tomita_run import *


class SimpleTomitaTest(unittest.TestCase):

    def test_tomita_person(self):
        dropall_and_create()
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.', type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita2('person.cxx', doc_id)
        key1 = '129:135'
        key3 = '0:16'
        value = 'Person'
        self.assertEqual(dic_out[key1], value)
        self.assertEqual(dic_out[key3], value)

    def test_tomita_person2(self):
        dropall_and_create()
        my_doc = Document(stripped='Следственный судья Киевского райсуда Харькова Валентина Божко удовлетворила ходатайство прокуратуры об аресте бывшего народного депутата от Компартии Украины Аллы Александровской, подозреваемой в сепаратизме, посягательстве на территориальную целостность Украины и попытке подкупа депутатов. "По решению суда подозреваемой в посягательстве на территориальную целостность и неприкосновенность, а также даче неправомерной выгоды служебному лицу, избрана мера пресечения в виде содержания под стражей на 2 месяца без определения суммы залога", - сообщила пресс-служба прокуратуры Харьковской области. В свою очередь адвокат А.Александровской Александр Шадрин заявил, что считает избранную меру пресечения необоснованной. "Это необоснованно. Конечно, мы будем подавать апелляцию", - сказал А.Шадрин корреспонденту агентства "Интерфакс-Украина". Как сообщалось, 28 июня адвокат А.Александровской А.Шадрин сообщил, что у его подзащитной прошел обыск и она была задержана. Ей инкриминируют ч.2 ст.110 (посягательство на территориальную целостность и неприкосновенность Украины) и ч.3 ст.369 (предложение, обещание или предоставление неправомерной выгоды служебному лицу) Уголовного кодекса Украины. 29 июня в СБУ подтвердили, что правоохранители задержали А.Александровскую, решается вопрос о ее аресте, а ее сын Александр, который скрывается в РФ, извещен о подозрении и объявлен в розыск. А.Александровская с 1996 года была бессменным первым секретарем Харьковского обкома КПУ, дважды избиралась депутатом Харьковского облсовета, четырежды – народным депутатом Украины. В 2008 году стала Почетным гражданином Харькова.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita2('person.cxx', doc_id)
        key1 = '158:178'
        key2 = '46:61'
        key3 = '639:655'
        key4 = '786:794'
        key5 = '891:899'
        key6 = '1249:1266'
        key7 = '1384:1401'
        value = 'Person'
        self.assertEqual(dic_out[key1], value)
        self.assertEqual(dic_out[key2], value)
        self.assertEqual(dic_out[key3], value)
        self.assertEqual(dic_out[key4], value)
        self.assertEqual(dic_out[key5], value)
        self.assertEqual(dic_out[key6], value)
        self.assertEqual(dic_out[key7], value)

    def test_tomita_date(self):
        dropall_and_create()
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita2('date.cxx', doc_id)
        key = '38:47'
        value = 'Date'
        self.assertEqual(dic_out[key], value)

    def test_tomita_loc(self):
        dropall_and_create()
        my_doc = Document(stripped='В Одинцовском районе Московской области правоохранители задержали троих квартирных воров.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita2('loc.cxx', doc_id)
        key = '2:20'
        value = 'Loc'
        self.assertEqual(dic_out[key], value)

    def test_tomita_adr(self):
        dropall_and_create()
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita2('adr.cxx', doc_id)
        key = '51:67'
        value = 'Adr'
        self.assertEqual(dic_out[key], value)

    def test_tomita_org(self):
        dropall_and_create()
        my_doc = Document(stripped='В разрешении спора некоторым образом принял участие и Конституционный суд РФ, приняв Определение от 05. 06. 03 N 276-о "Об отказе в принятии к рассмотрению запроса мирового судьи 113-го судебного участка города Санкт-Петербурга. Журнал Forbes оценивает её состояние в 2,7 млрд долларов.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita2('org.cxx', doc_id)
        key = '54:73'
        key2 = '236:242'
        value = 'Org'
        self.assertEqual(dic_out[key], value)
        self.assertEqual(dic_out[key2], value)

    def test_tomita_norm_act(self):
        dropall_and_create()
        my_doc = Document(stripped='''В Забайкалье судить будут организаторов незаконного игорного бизнеса из Читы.
Подпольный клуб работал в съемной квартире в центре города. В него могли попасть только постоянные клиенты, среди которых были даже пенсионеры. Заведение никогда не пустовало, сообщили в УМВД по краю.
При обысках оперативники изъяли моноблоки, ноутбуки и роутеры, с помощью которых игроки выходили в сеть для азартных игр.
Следователи СУ СКР по Забайкалью завели на организатора казино и 5 его помощников, обеспечивающих круглосуточную работу клуба, уголовное дело по ч.2 ст.171.2 УК РФ.
На период следствия все подозреваемые были на подписке о невыезде. Сейчас расследование завершили, уголовное дело направили в суд.''', type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        print(doc_id)
        dic_out = run_tomita2('norm_act.cxx', doc_id)
        print(dic_out)
        key1 = '546:562'
        value = '07be43b9-8eba-400c-aede-d6ca88a34e12'
        self.assertEqual(dic_out[key1], value)

    def test_tomita_profession(self):
        dropall_and_create()
        my_doc = Document(stripped=' Конечно, мы будем подавать апелляцию", - сказал адвокат А.Шадрин корреспонденту агентства "Интерфакс-Украина".',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita2('prof.cxx', doc_id)
        key1 = '49:56'
        key2 = '66:80'
        value = 'Prof'
        self.assertEqual(dic_out[key1], value)
        self.assertEqual(dic_out[key2], value)
