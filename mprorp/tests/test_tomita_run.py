import unittest

from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.tomita.tomita_run import run_tomita


class SimpleTomitaTest(unittest.TestCase):

    def test_tomita_person(self):
        dropall_and_create()
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.', type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita('person.cxx',doc_id)
        key1 = '129:135'
        key3 = '0:16'
        value = 'Person'
        self.assertEqual(dic_out[key1], value)
        self.assertEqual(dic_out[key3], value)

    def test_tomita_date(self):
        dropall_and_create()
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita('date.cxx',doc_id)
        key = '38:47'
        value = 'Date'
        self.assertEqual(dic_out[key], value)

    def test_tomita_loc(self):
        dropall_and_create()
        my_doc = Document(stripped='В Одинцовском районе Московской области правоохранители задержали троих квартирных воров.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita('loc.cxx', doc_id)
        print(dic_out)
        key = '2:20'
        value = 'Loc'
        self.assertEqual(dic_out[key], value)

    def test_tomita_adr(self):
        dropall_and_create()
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita('adr.cxx', doc_id)
        key = '51:67'
        value = 'Adr'
        self.assertEqual(dic_out[key], value)

    def test_tomita_org(self):
        dropall_and_create()
        my_doc = Document(stripped='В разрешении спора некоторым образом принял участие и Конституционный суд РФ, приняв Определение от 05. 06. 03 N 276-о "Об отказе в принятии к рассмотрению запроса мирового судьи 113-го судебного участка города Санкт-Петербурга.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita('org.cxx', doc_id)
        key = '54:73'
        value = 'Org'
        self.assertEqual(dic_out[key], value)