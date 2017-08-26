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
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup, convert_tomita_result_to_markup2
from sqlalchemy.orm.attributes import flag_modified

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


def spot_urls(text):
    return re.findall('(http.*?)"', text)


def collect_urls():
    line = ''
    docs = session.query(Document).filter(Document.status == 76).all()
    for doc in docs:
        rubrics = session.query(DocumentRubric).filter(DocumentRubric.doc_id == doc.doc_id).all()
        if len(rubrics) == 0:
            rub_line = '0   0'
        else:
            rubrics = [i.rubric_id for i in rubrics]
            if '14e511c0-2ce9-49b2-9d0c-f16c383765d1' in str(rubrics):
                rub_line = '1   '
            else:
                rub_line = '0   '
            if 'db9baa28-e201-47a6-aada-14f44f42e98f' in str(rubrics):
                rub_line += '1'
            else:
                rub_line += '0'
        urls = spot_urls(doc.doc_source)
        for url in urls:
            line += url + ' ' + rub_line + '\n'
    return line

def rename_norm_acts():
    norm_acts = session.query(Entity).filter(Entity.entity_class == 'norm_act').all()
    print(len(norm_acts))
    norm_acts = [i for i in norm_acts if 'UC' in i.name or 'KOAP' in i.name]
    print(len(norm_acts))
    for act in norm_acts:
        act.name = act.name.replace('UC', 'УК').replace('KOAP', 'КоАП')
        session.commit()

def locality_import(type):
    kladr = session.query(KLADR).filter(KLADR.type == type).all()
    print(len(kladr))
    for i in kladr:
        external_data = {'kladr_level': i.level, 'kladr_type': i.type, 'kladr_id': i.kladr_id, 'name_lemmas': i.name_lemmas}
        data = {'name': i.name, 'loc_type': 'населенный пункт'}
        new_entity = Entity(name=i.name, entity_class='location', external_data=external_data, data=data)
        session.add(new_entity)
        session.commit()

def delete_entity2(entity, session=None):
    if session is None:
        session = Driver.db_session()
    session.query(Entity).filter(Entity.entity_id == entity.entity_id).delete()
    session.commit()

def delete_same(locs, session=None):
    if session is None:
        session = Driver.db_session()
    names = [i.name for i in locs if i.name != '']
    print(len(names), len(set(names)))
    for name in names:
        if names.count(name) > 1:
            print(name)
            entities = session.query(Entity).filter(Entity.name == name).all()
            print(len(entities))
            good = entities[0]
            for entity in entities[1:]:
                markups = session.query(Reference).filter(Reference.entity == entity.entity_id).all()
                if markups is []:
                    delete_entity2(entity)
                else:
                    for markup in markups:
                        if session is None:
                            session = Driver.db_session()
                        markup.entity = good.entity_id
                        session.commit()
                    delete_entity2(entity)
            print(len(session.query(Entity).filter(Entity.name == name).all()))

def update_locality_and_jail():
    locs = session.query(Entity).filter(Entity.entity_class == 'location').all()
    to_upd = [i for i in locs if 'kladr_id' in i.data]
    print('locs', len(to_upd))
    for loc in to_upd:
        external_data = loc.data
        new_data = {'name': loc.name, 'loc_type': 'населенный пункт'}
        loc.data = new_data
        loc.external_data = external_data
        session.commit()
    jails = session.query(Entity).filter(Entity.data["type"].astext == 'тюрьма').all()
    print('jails', len(jails))
    for jail in jails:
        external_data = jail.data
        jail.data = {'name': jail.name, 'jurisdiction': '', 'location': '', 'org_type': 'тюрьма'}
        jail.external_data = external_data
        session.commit()
    delete_same(session.query(Entity).filter(Entity.data['org_type'].astext == 'тюрьма'))
    delete_same(session.query(Entity).filter(Entity.external_data['kladr_type'].astext == 'Город'))

#j = Entity()
#j.name = 'ИК-16 Краснотурьинск'
#j.data = {'name': 'ИК-16 Краснотурьинск', 'jurisdiction': '', 'location': '', 'org_type': 'jail'}
#j.external_data = {'norm': ['ик-16 краснотурьинск'], 'type': 'jail', 'names': ['ИК-16 Краснотурьинск'], 'url': '/catalog/object/ik16kras/'}
#session.add(j)
#session.commit()
#jl = eval(open('jail_locations.json', 'r', encoding='utf-8').read(), {})
#jails = session.query(Entity).filter(Entity.data['org_type'].astext == 'jail').all()
#jails = [i for i in jails if i.data['location'] == '']
#print(len(jails))
#for jail in jails:
#    if jail.name in jl:
#        print(jail.name)
#        jail.data['location'] = jl[jail.name]
#        flag_modified(jail, 'data')
#        session.commit()
#    else:
#        print('bad name', jail.name, jail.external_data['url'])

a = [i for i in session.query(Entity).filter(Entity.data['org_type'].astext == 'тюрьма').all()]
print(len(a))
#for i in a:
#    if i.data["jurisdiction"] == '':
#        i.data["jurisdiction"] = []
#    elif i.data["jurisdiction"] == [[]]:
#        i.data["jurisdiction"] = []
#
#    if i.data["location"] == '':
#        i.data["location"] = []
#    elif i.data["location"] == [[]]:
#        i.data["location"] = []
#
#    if i.data["location"] != []:
#        loc = [i for i in session.query(Entity).filter(Entity.name == i.data["location"][0]).all() if i.external_data is not None]
#        if len(loc) > 1:
#            print(loc[0].name)
#        elif len(loc) == 1:
#            i.data["location"] = [str(loc[0].entity_id)]
#            flag_modified(i, 'data')
#            session.commit()
#a = [i for i in session.query(Entity).filter(Entity.data['org_type'].astext == 'тюрьма').all() if i.data['jurisdiction'] == '']
#print(len(a))
#for i in a:
#    if i.data['location'] != [] and str(i.data['location']).count('-') > 2:
#        loc = session.query(Entity).filter(Entity.entity_id == i.data['location'][0]).all()
#        if len(loc) == 1:
#            i.external_data['location'] = loc[0].name
#            flag_modified(i, 'external_data')
#            session.commit()
#        else:
#            print(i.entity_id)

#update_locality_and_jail()
#f1('jails')
#jail = session.query(Entity).filter(Entity.name.contains('СИЗО-2 Лефортово')).first()
#print(jail.external_data)
#doc = Document()
#doc.stripped = '''Первенство УФСИН России по Алтайскому краю среди кинологов со служебными собаками прошло в поселке Куета, сообщает ведомство.
#Кинологи и их питомцы выполняли различные задания, в том числе силовое задержание нарушителя. По итогам первое место взяли сотрудники "тройки" - Исправительной колонии № 3 в Барнауле.
#Фото: Андрей Луковский.'''
#jail = session.query(Entity).filter(Entity.entity_id == 'da796201-a4b7-459a-9e18-a2527f91690a').first()
#print(jail.external_data)
record = session.query(Record).filter(Record.document_id == '66047987-668f-0e5b-8771-ea07a48335c0').first()
print(record.source)
doc = session.query(Document).filter(Document.doc_id == record.source).first()
print(run_tomita(doc, 'jail.cxx'))
#used = delete_old_locations()
#print('Markup changed')
#print(len(used))
#for entity_id in used:
#    session.query(Entity).filter(Entity.entity_id == entity_id).delete()
#    session.commit()
#rename_norm_acts()
#norm_acts = session.query(Entity).filter(Entity.name == 'Москва').all()
#for i in norm_acts:
#    print(i.data)
#print(len(norm_acts))
#norm_acts = [i for i in norm_acts if 'art' not in i.data]
#print(len(norm_acts))
#for act in norm_acts:
#    act.data = norm_data[act.name]
#    session.commit()
#x = open('norm_acts_data.py', 'w', encoding='utf-8')
#x.write('norm_data = ' + str(upd_norm_acts()))
#x.close()
#print(collect_urls())
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
#doc = session.query(Document).filter(Document.doc_id == '000166cf-826a-478b-b01a-229eb755d1cf').first()
#print(run_tomita(doc, 'locality.cxx'))
#print(get_meta(doc))