#from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.data.kladr import mvd_root
from mprorp.tomita.tomita_run_ovd import run_tomita_ovd
import re

session = db_session()
#object = session.query(Entity).filter(Entity.external_data['kladr'].astext == "77000000000062700").all()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()

#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()

a = session.query(Document).filter(Document.doc_id == '521d71f9-907e-4547-bfe1-77cc789e0220').all()
#print(len(a))
out = run_tomita_ovd(a[0], n=1)
print(out)
#for text in a:
#    print(text.doc_id)
#    out = run_tomita_ovd(text)
#    print(out)
#    print('\n')