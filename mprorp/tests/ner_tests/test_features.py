import unittest

from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.tomita.tomita_run import run_tomita
import mprorp.analyzer.rubricator as rb
import mprorp.ner.feature as ner_feature
import mprorp.analyzer.db as db


class SimpleTomitaTest(unittest.TestCase):

    def test_tomita_person(self):
        dropall_and_create()
        my_doc = Document(stripped='Алексей Бочкарев был задержан вечером 8 августа на Манежной площади за плакат, который, по мнению сотрудников полиции, оскорблял Путина.', type='article')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        dic_out = run_tomita('person.cxx',doc_id)
        rb.morpho_doc(doc_id)
        ner_feature.create_tomita_feature(doc_id, ['date.cxx', 'person.cxx'])
        gaz_id = db.put_gazetteer('gaz1', ['площадь', 'улица', 'переулок'])
        ner_feature.create_gazetteer_feature(doc_id, gaz_id)
        print(db.get_ner_feature(doc_id))