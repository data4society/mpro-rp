import sys
sys.path.insert(0, '..')
from mprorp.utils import home_dir
from mprorp.analyzer.db import *
from mprorp.controller.init import global_mystem as mystem


def normalization(name):
    norm = ''
    for n in mystem.lemmatize(name):
        if n != '\n':
            norm += n
    return norm


def put_court():
    session = db_session()
    print('Import START')
    courts = eval(open(home_dir + '/court/court_full.json', 'r', encoding='utf-8').read(), {})
    for court in courts:
        a = Entity()
        a.name = court['full name'] + ' (' + court['adr'].split(',')[0] + ')'
        a.data = {'location': '', 'jurisdiction': '', 'org_type': 'court', 'name': court['full name']}
        a.external_data = {'norm': normalization(court['full name']), 'type': court['type'], "cut name": court['name'],
                           'adr': court['adr']}
        a.entity_class = 'org'
        session.add(a)
        session.commit()
    print('Import DONE')

put_court()
