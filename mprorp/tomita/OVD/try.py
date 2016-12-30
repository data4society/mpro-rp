#from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
#from mprorp.db.models import *
#from mprorp.data.kladr import mvd_root
from mprorp.tomita.tomita_run import *
from mprorp.ner.tomita_to_markup import *
from mprorp.analyzer.db import *
import re
from mprorp.analyzer.f1_for_ovd import f1

session = db_session()
#object = session.query(Entity).filter(Entity.external_data['kladr'].astext == "77000000000062700").all()
#!!!!ЗАНЧЕНИЯ КЛЮЧА РАВНО ... a = session.query(Entity).filter(Entity.data["jurisdiction"].astext == mvd_root).all()
#!!!!СТРОКА СОДЕРЖИТ СТРОКУ a = session.query(Document).filter(Document.stripped.contains('отдел полиции №3')).all()

def try_ovd(doc_id=None, source_id=None):
    if source_id is not None:
        doc_id = session.query(Record).filter(Record.document_id == source_id).first().source
    a = session.query(Document).filter(Document.doc_id == doc_id).all()
    print(a[0].doc_id)
    out = run_tomita(a[0], 'ovd.cxx')
    print(out)
    if out == {}:
        print('No OVD')
    else:
        for i in out:
            ovd = session.query(Entity).filter(Entity.entity_id == out[i]).first()
            print(out[i], ovd.name, ovd.external_data['kladr'])


try_ovd(source_id='037a40d6-3d29-bdc7-a0c5-20e527aa3773')
#print(f1())
#print(session.query(Entity).filter(Entity.external_data['kladr'].astext == '63000005000003400').first().entity_id)
#print(session.query(Entity).filter(Entity.external_data['kladr'].astext == '61000001000031700').first().name)
#a = get_ner_feature_dict('23d197c3-467e-49d8-8a07-5336ec2b18fe', 'fb8fc548-0464-40b7-a998-04a6e1b95eb6', 'Person')
#a = get_ner_feature_one_feature_dict('00000f42-e066-4062-b380-1a3361e66c64', 'Person', session)
#print(a)
#new_entity = Entity(name='KOAP', entity_class='norm_act', data={'Matvey_try':1})
#session.add(new_entity)
#session.commit()
#a = session.query(Entity).filter(Entity.entity_class == 'norm_act').all()
#print(len(a))
#for entity in a:
#    db.delete_entity(entity.entity_id)
#docs = session.query(Document).filter_by(app_id='ovd_test').options(load_only("doc_id")).all()
#print(len(docs))