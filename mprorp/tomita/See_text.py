from mprorp.utils import home_dir
import os
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.tomita.OVD.code_from_db import *

#text = get_doc('f844e3f0-4b02-4643-9ee3-2bdcd7c422be')
#print(text)
#x = open('C:/Users/User/Desktop/try.txt', 'w', encoding='utf-8')
#x.write('1')
#x.close()
#print(os.path.dirname(os.path.realpath(__file__)))
#path = os.path.dirname(os.path.realpath(__file__))
#os.chdir(path + '/grammars')
session = db_session()
fact = {'sn': 17, 'facts': {'Location': [0, 4]}, 'type': 'LocationFact', 'string': 'крыму', 'id': 22, 'fs': 2597, 'norm': {'Location': ['крым', 'спасск-дальний']}}
for i in get_codes_for_fact(fact, session):
    for ii in i:
        print(ii.name, ii.name_lemmas)
#all_levels += session.query(KLADR).filter_by(level=2).all()
#print(a)
#type1 = session.query(KLADR.kladr_id).filter_by(name_lemmas='{"строитель": 1}').all()
#a = []
#a += session.query(KLADR).filter(KLADR.name_lemmas.has_key("москва"), KLADR.name_lemmas.has_key("автомагистраль")).all()
#for i in a:
#    print(i)
#type3 = session.query(KLADR).filter_by(level=3).all()
#for i in type2:
#    if i in type3:
#        print(i)
#fact2 = {'sn': 8, 'facts': {'type_2': [0, 9]}, 'type': 'LocationFact', 'string': 'ленинскому', 'id': 8, 'fs': 864, 'norm': {'type_2': ['ленинский']}}
#a = get_codes_for_fact(fact2)
#for i in a:
#    for el in i:
#        print(el.name)