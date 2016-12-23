import sys
sys.path.insert(0, '..')
from mprorp.utils import home_dir
from mprorp.analyzer.db import *

koap__file_path = home_dir + '/norm_act/table.csv'
session = db_session()
f = open(koap__file_path, 'r', encoding='utf-8')
print('KoAP import START')
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
    new_entity = Entity(name='KOAP', entity_class='norm_act', data=data)
    session.add(new_entity)
    session.commit()
print('KoAP import DONE')