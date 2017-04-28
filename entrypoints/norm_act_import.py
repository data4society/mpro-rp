import sys
sys.path.insert(0, '..')
from mprorp.utils import home_dir
from mprorp.analyzer.db import *

koap_file_path = home_dir + '/norm_act/table.csv'
uc_file_path = home_dir + '/norm_act/table2.csv'
koap_file_path_new = home_dir + '/norm_act/table_new.csv'
uc_file_path_new = home_dir + '/norm_act/table2_new.csv'
koap_file_path_only_arts = home_dir + '/norm_act/table_only_arts.csv'
uc_file_path_only_arts = home_dir + '/norm_act/table2_only_arts.csv'


def put_norm_act(path):
    session = db_session()
    f = open(path, 'r', encoding='utf-8')
    print('Import START')
    for line in f:
        line = line.strip()
        line = line.split('@@')
        data = {'art' : line[0],
                'art_name' : line[1],
                'art_text' : line[6],
                'part' : line[2],
                'part_text' : line[3],
                'punct' : line[4],
                'punct_text' : line[5]}
        if 'table2' not in path:
            new_entity = Entity(name='KOAP', entity_class='norm_act', data=data)
        else:
            new_entity = Entity(name='UC', entity_class='norm_act', data=data)
        session.add(new_entity)
        session.commit()
    print('Import DONE')

def put_norm_act_new(path):
    session = db_session()
    f = open(path, 'r', encoding='utf-8')
    print('Import START')
    for line in f:
        line = line.strip()
        line = line.split('@@')
        if line[4] == '0':
            data = {'art' : line[0],
                    'art_name' : line[1],
                    'art_text' : line[5],
                    'part' : line[2],
                    'part_text' : line[3],
                    'puncts' : line[4]}
        else:
            puncts = line[4].replace('#', '; ').replace('__', ')').replace(';;', ';')
            data = {'art': line[0],
                    'art_name': line[1],
                    'part': line[2],
                    'part_text': line[3],
                    'puncts': puncts}
        if 'table2' not in path:
            new_entity = Entity(name='KOAP ' + line[0] + ' ' + line[2], entity_class='norm_act', data=data)
        else:
            new_entity = Entity(name='UC ' + line[0] + ' ' + line[2], entity_class='norm_act', data=data)
        session.add(new_entity)
        session.commit()
    print('Import DONE')

def put_norm_act_only_art(path):
    session = db_session()
    f = open(path, 'r', encoding='utf-8')
    print('Import START')
    for line in f:
        line = line.strip()
        line = line.split('@@')
        data = {'art': line[0],
                'art_name': line[1],
                'art_text': line[2]}
        if 'table2' not in path:
            new_entity = Entity(name='KOAP ' + line[0], entity_class='norm_act', data=data)
        else:
            new_entity = Entity(name='UC ' + line[0], entity_class='norm_act', data=data)
        session.add(new_entity)
        session.commit()
    print('Import DONE')


def upd_norm_acts(idd=None):
    session = db_session()
    if idd is None:
        norm_acts = session.query(Entity).filter(Entity.entity_class == 'norm_act').all()
    else:
        norm_acts = session.query(Entity).filter(Entity.entity_id == idd).all()
    print(len(norm_acts))
    norm_acts = [i for i in norm_acts if 'article' not in i.data]
    print(len(norm_acts))
    for act in norm_acts:
        try:
            new_data = {}
            new_data["art"] = act.data["art"]
            if "art_text" in act.data:
                new_data["art_text"] = act.data["art_text"]
            new_data["art_name"] = act.data["art_name"]
            if 'KOAP' in act.name:
                new_data['code'] = 'КоАП'
                new_data['parent'] = str(session.query(Entity).filter(Entity.name == 'KOAP ' +
                                                                      new_data['art']).first().entity_id).replace('UUID(', '').replace(')', '')
            else:
                new_data['code'] = 'УК'
                try:
                    new_data['parent'] = str(session.query(Entity).filter(Entity.name == 'UC ' +
                                                                      new_data['art'][:-1]).first().entity_id).replace('UUID(', '').replace(')', '')
                except:
                    new_data['parent'] = str(session.query(Entity).filter(Entity.name == 'UC ' +
                                                                          new_data['art']).first().entity_id).replace('UUID(', '').replace(')', '')
            if 'part_text' in act.data:
                new_data["puncts"] = act.data["puncts"]
                new_data["part"] = act.data["part"]
                new_data["part_text"] = act.data["part_text"]
                new_data['content'] = new_data['part_text']
                new_data['article'] = new_data['art_name']
            else:
                new_data['content'] = new_data['art_text']
                new_data['article'] = new_data['art_name']
            act.data = new_data
            session.commit()
        except:
            print(act.entity_id)
    print('UPD Done')

put_norm_act_new(koap_file_path_new)
put_norm_act_new(uc_file_path_new)
put_norm_act_only_art(uc_file_path_only_arts)
put_norm_act_only_art(koap_file_path_only_arts)
upd_norm_acts()