#from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *
#from mprorp.data.kladr import mvd_root
from mprorp.tomita.tomita_run import *
#from mprorp.ner.tomita_to_markup import *
import re

session = db_session()
#object = session.query(Entity).filter(Entity.external_data['kladr'].astext == "77000000000062700").all()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()

#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()

a = session.query(Document).filter(Document.doc_id == 'd3488171-a773-4edf-ab20-b8f9118f1c32').all()
#run_tomita2('ovd.cxx', '5cfe3531-9261-48e3-b5be-421a1d89b678')
#out = convert_tomita_result_to_markup(a[0], ['person.cxx'])
#out = convert_tomita_result_to_markup(a[0], ['ovd.cxx'])
for text in a:
    print(text.doc_id)
    out = run_tomita(text, 'ovd.cxx')
    print(out)
#    print('\n')