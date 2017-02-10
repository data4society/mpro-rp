#from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
#from mprorp.db.models import *
#from mprorp.data.kladr import mvd_root
from mprorp.tomita.tomita_run import *
from mprorp.tomita.tomita_out import clean_act
from mprorp.ner.tomita_to_markup import *
from mprorp.analyzer.db import *
import re
from mprorp.analyzer.f1_for_ovd import f1
from mprorp.tomita.norm_act.global_identification import act_identification
import os

session = db_session()
#object = session.query(Entity).filter(Entity.external_data['kladr'].astext == "77000000000062700").all()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()
#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()

def try_ovd(doc_id):
    a = session.query(Document).filter(Document.doc_id == doc_id).all()
    out = run_tomita(a[0], 'ovd.cxx')
    print(out)
    if out == {}:
        print('No OVD')
    else:
        for i in out:
            ovd = session.query(Entity).filter(Entity.entity_id == out[i]).first()
            print(out[i], ovd.name, ovd.external_data['kladr'])

def try_norm_act(source_id):
    doc = session.query(Record).filter(Record.document_id == source_id).first()
    doc_id = doc.source
    a = session.query(Document).filter(Document.doc_id == doc_id).first()
    print(a.doc_id)
    b = run_tomita(a, 'norm_act.cxx')
    print(b)
    print('---------')
    for i in b:
        act = session.query(Entity).filter(Entity.entity_id == b[i]).first()
        print(act.name)
        print('---------')
    print(doc.entities)

def entity_delition(entity_class):
    a = session.query(Entity).filter(Entity.entity_class == entity_class).all()
    print(len(a))
    for entity in a:
        db.delete_entity(entity.entity_id)

def add_norm_act(norm_act):
    session.add(norm_act)
    session.commit()

#try_ovd('7a711bb1-08ab-473d-b37d-d126dc887c9a')
#f1()
try_norm_act('293573c5-7d82-fbdb-c88d-7dfa4ecd25f7')
#doc = session.query(Document).filter(Document.doc_id == '6e5dad1a-ff04-4ba4-9b17-2d3bd5e75d14').first()
#print(session.query(Record).filter(Record.app_id == 'ovd_ideal', Record.document_id == '0c269563-5b0b-2695-a9f5-cdade7d2f3c8').all())
#print(session.query(Entity).filter(Entity.external_data['kladr'].astext == '61000001000031700').first().name)
#a = get_ner_feature_dict('23d197c3-467e-49d8-8a07-5336ec2b18fe', 'fb8fc548-0464-40b7-a998-04a6e1b95eb6', 'Person')
#a = get_ner_feature_one_feature_dict('00000f42-e066-4062-b380-1a3361e66c64', 'Person', session)
#print(a)
#new_entity = Entity(name='KOAP', entity_class='norm_act', data={'Matvey_try':1})
#session.add(new_entity)
#session.commit()
#entity_delition('norm_act')
#start_tomita('date.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6')
#print(run_tomita2('date.cxx', 'c8236b7e-b0a3-43c1-8601-cb57a055189d', status=0))
#print(run_tomita2('person.cxx', 'c8236b7e-b0a3-43c1-8601-cb57a055189d', status=0))
#print(run_tomita2('loc.cxx', 'c8236b7e-b0a3-43c1-8601-cb57a055189d', status=0))
#print(run_tomita2('ovd.cxx', 'c8236b7e-b0a3-43c1-8601-cb57a055189d', status=0))
#print(run_tomita2('norm_act.cxx', 'c8236b7e-b0a3-43c1-8601-cb57a055189d', status=0))
#n = session.query(Entity).filter(Entity.entity_class == 'norm_act').all()
#for a in n:
#    a.name = a.name + ' ' + a.data['art'][:-1] + ' ' + a.data['part'][:-1]
#session.commit()