#from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.data.kladr import mvd_root
from mprorp.tomita.tomita_run_ovd import run_tomita_ovd
from mprorp.tomita.tomita_run import *
from mprorp.ner.tomita_to_markup import *
import re

session = db_session()
#object = session.query(Entity).filter(Entity.external_data['kladr'].astext == "77000000000062700").all()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()

#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()

a = session.query(Document).filter(Document.doc_id == '0229dc23-91cd-4645-9035-63702652a4a3').all()
#run_tomita2('ovd.cxx', '521d71f9-907e-4547-bfe1-77cc789e0220')
#out = convert_tomita_result_to_markup(a[0], ['person.cxx'])
#out = convert_tomita_result_to_markup(a[0], ['ovd.cxx'])
for text in a:
    print(text.doc_id)
    out = run_tomita(text, 'ovd.cxx')
    print(out)
#    print('\n')