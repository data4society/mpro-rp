#from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.data.kladr import mvd_root
from mprorp.tomita.tomita_run_ovd import run_tomita_ovd
import re

session = db_session()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()

#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()
a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()
out = run_tomita_ovd(a[0])
print(out)

#a = re.findall('<([A-z]*?)_TOMITA val="(.*?)"/>', '<OVD_TOMITA val="ОТДЕЛ ПОЛИЦИИ"/><Numb_TOMITA val="1"/>')
#print(a)
