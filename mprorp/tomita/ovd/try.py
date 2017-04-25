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
from mprorp.tomita.tomita_run_loc_c import run_tomita_loc_c
from mprorp.tomita.locality.meta_loc import get_meta

session = db_session()
#object = session.query(Entity).filter(Entity.external_data['kladr'].astext == "77000000000062700").all()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()
#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()

def try_ovd(doc_id):
    a = session.query(Document).filter(Document.doc_id == doc_id).all()
    out = run_tomita(a[0], 'ovd.cxx')
    print(out)
    if out == {}:
        print('No ovd')
    else:
        for i in out:
            ovd = session.query(Entity).filter(Entity.entity_id == out[i]).first()
            print(out[i], ovd.name, ovd.external_data['kladr'])

def try_all_ovd():
    bad_docs = []
    a = session.query(Document).filter(Document.app_id == 'ovd_test').all()
    print(len(a))
    for doc in a:
        try:
            out = run_tomita(doc, 'ovd.cxx')
        except:
            bad_docs.append(str(doc.doc_id))
    print('BAD DOCS: ' + str(bad_docs))

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

#try_all_ovd()
#f1('ovd')
#try_ovd('33456708-ef5c-4fc7-aa5e-733a21df530c')
#f1('normacts')
#try_norm_act('f37e7619-7565-7af8-3236-64ad5532b008')
#doc = session.query(Document).filter(Document.doc_id == '6e5dad1a-ff04-4ba4-9b17-2d3bd5e75d14').first()
#for i in list(set(session.query(KLADR).filter(KLADR.type == 'Город').all())):
#    print(i.name)
#print(session.query(Entity).filter(Entity.entity_id == '594f2d02-175b-41af-b0e0-68bcfb8b3cce').first().name)
#a = get_ner_feature_dict('23d197c3-467e-49d8-8a07-5336ec2b18fe', 'fb8fc548-0464-40b7-a998-04a6e1b95eb6', 'Person')
#a = get_ner_feature_one_feature_dict('00000f42-e066-4062-b380-1a3361e66c64', 'Person', session)
#print(a)
#new_entity = session.query(Entity).filter(Entity.entity_id == '00095571-1ade-47c1-81ab-2b74dcf6b035').first()
#new_entity.data = {'try' : 'Matvey'}
#print(new_entity)
##session.add(new_entity)
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
doc = session.query(Document).filter(Document.doc_id == '000166cf-826a-478b-b01a-229eb755d1cf').first()
print(run_tomita(doc, 'locality.cxx'))
#print(get_meta(doc))