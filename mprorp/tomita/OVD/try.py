#from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
#from mprorp.db.models import *
#from mprorp.data.kladr import mvd_root
from mprorp.tomita.tomita_run import *
from mprorp.ner.tomita_to_markup import *
from mprorp.analyzer.db import *
import re

session = db_session()
#object = session.query(Entity).filter(Entity.external_data['kladr'].astext == "77000000000062700").all()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()
#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()
def try_ovd(doc_id):
    a = session.query(Document).filter(Document.doc_id == doc_id).all()
    print(a[0].doc_id)
    run_tomita2('ovd.cxx', doc_id)
    #out = convert_tomita_result_to_markup(a[0], ['person.cxx'])
    out = convert_tomita_result_to_markup(a[0], ['ovd.cxx'])
    #out = run_tomita(a[0], 'ovd.cxx')
    #print(out)
    #print('\n')

try_ovd('a904c4b7-973a-498f-a941-78627d0393e8')
#print(session.query(Entity).filter(Entity.external_data['kladr'].astext == '63000005000003400').first().entity_id)
#print(session.query(Entity).filter(Entity.external_data['kladr'].astext == '63028000044003100').first().name)
#a = get_ner_feature_dict('23d197c3-467e-49d8-8a07-5336ec2b18fe', 'fb8fc548-0464-40b7-a998-04a6e1b95eb6', 'Person')
#a = get_ner_feature_one_feature_dict('00000f42-e066-4062-b380-1a3361e66c64', 'Person', session)
#print(a)