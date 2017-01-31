import sys
sys.path.insert(0, '..')
from mprorp.utils import home_dir
from mprorp.analyzer.db import *

koap_file_path = home_dir + '/norm_act/table.csv'
uc_file_path = home_dir + '/norm_act/table2.csv'
koap_file_path_new = home_dir + '/norm_act/table_new.csv'
uc_file_path_new = home_dir + '/norm_act/table2_new.csv'


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
                    'art_text': line[5],
                    'part': line[2],
                    'part_text': line[3],
                    'puncts': puncts}
        if 'table2' not in path:
            new_entity = Entity(name='KOAP', entity_class='norm_act', data=data)
        else:
            new_entity = Entity(name='UC', entity_class='norm_act', data=data)
        session.add(new_entity)
        session.commit()
    print('Import DONE')

put_norm_act_new(koap_file_path_new)
put_norm_act_new(uc_file_path_new)