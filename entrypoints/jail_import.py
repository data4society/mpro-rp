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


def put_jail():
    session = db_session()
    print('Import START')
    jails = open(home_dir + '/jail/jail.json', 'r', encoding='utf-8').read()
    #jails = open('jail.json', 'r', encoding='utf-8').read()
    jails = eval(jails, {})
    jails_db = [i.name for i in session.query(Entity).filter(Entity.data["type"].astext == 'jail').all()]
    print(len(jails_db))
    for idd in jails:
        jail = jails[idd]
        if jail['name'] not in jails_db:
            names = [jail['name']]
            for key in jail.keys():
                if key != 'name' and key != 'url':
                    names += jail[key]
            norm = [normalization(i) for i in names]
            new_entity = Entity(name=jail['name'], entity_class='org', data={'names': names, 'url': jail['url'],
                                                                             'type': 'jail', 'norm': norm})
            session.add(new_entity)
            session.commit()
        else:
            print(jail['name'])
    print('Import DONE')

put_jail()