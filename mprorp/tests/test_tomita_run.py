import unittest
from mprorp.db.dbDriver import *
from mprorp.tomita_grammars.test_tomita.tomita_run import run_tomita

class SimpleTomitaTest(unittest.TestCase):

    def test_tomita_person(self):
        dropall_and_create()
        key1 = '180:188'
        key2 = '440:449'
        key3 = '0:16'
        value = 'Person'
        dic_out = run_tomita('person.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6')
        self.assertEqual(dic_out[key1], value)
        self.assertEqual(dic_out[key2], value)
        self.assertEqual(dic_out[key3], value)

    def test_tomita_date(self):
        dropall_and_create()
        key = '38:47'
        value = 'Date'
        dic_out = run_tomita('date.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6')
        self.assertEqual(dic_out[key], value)

