import sys
sys.path.insert(0, '..')
from mprorp.utils import home_dir
from mprorp.analyzer.db import *

koap_file_path = home_dir + '/norm_act/table.csv'
uc_file_path = home_dir + '/norm_act/table2.csv'

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

put_norm_act(koap_file_path)
put_norm_act(uc_file_path)