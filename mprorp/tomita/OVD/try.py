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

def try_ovd(source_id=None):
    doc = session.query(Record).filter(Record.document_id == source_id).first()
    doc_id = doc.source
    url = doc.url
    ideal_id = re.findall('documentId=(.*?),app=ovd_ideal', url)[0]
    a = session.query(Document).filter(Document.doc_id == doc_id).all()
    print(a[0].doc_id)
    out = run_tomita(a[0], 'ovd.cxx')
    if out == {}:
        print('No OVD')
    else:
        for i in out:
            ovd = session.query(Entity).filter(Entity.entity_id == out[i]).first()
            print(out[i], ovd.name, ovd.external_data['kladr'])
    print('\noriginal')
    print(session.query(Record).filter(Record.app_id == 'ovd_ideal', Record.document_id == ideal_id).first().entities)


try_ovd(source_id='d6467f9d-31fe-584f-1984-abf55444c0f2')
#print(f1())
#print(session.query(Record).filter(Record.app_id == 'ovd_ideal', Record.document_id == '0c269563-5b0b-2695-a9f5-cdade7d2f3c8').all())
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

