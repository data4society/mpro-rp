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


doc = session.query(Document).filter(Document.doc_id == '00037072-cf48-42ee-a9d9-061e5b558328').first()
doc.stripped = '''В российском СИЗО украинскому политзаключенному и журналисту Роману Сущенко запретили отправлять письма украинским дипломатам и президенту
Об этом сообщает Укринформ со ссылкой на адвоката Марка Фейгина.
-Был сегодня в СИЗО у Романа Сущенко. Узнал, что цензура не пропустила его письма, отправленные обычной почтой президенту Петру Порошенко, главе МИД Павлу Климкину и украинскому консулу в Москве Геннадию Брескаленко… Я не очень понимаю, по каким причинам это сделано, и никаких объяснений мне не дают. На мой взгляд, это ущемляет права моего подзащитного, — сказал Фейгин.
Адвокат также отметил, что в СИЗО «Лефортово» поступает большое количество писем для Сущенко, но ему передают только малую часть из них.
В связи с этим, Фейгин обратиться с жалобой в Генпрокуратуру РФ.
Как сообщал Соцпортал, Сущенко в СИЗО написал письмо президенту.'''
print(run_tomita(doc, 'jail.cxx'))
#rename_norm_acts()
#norm_acts = session.query(Entity).filter(Entity.entity_class == 'norm_act').all()
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