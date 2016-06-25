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
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.',type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita('loc.cxx', doc_id)
        key = '51:67'
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