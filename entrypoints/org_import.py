import sys
sys.path.insert(0, '..')
from mprorp.utils import home_dir
from mprorp.analyzer.db import *
import re

path1 = home_dir + '/orgs/orgs_eng.txt'
path2 = home_dir + '/orgs/orgs_rus.txt'
path3 = home_dir + '/orgs/org_try.txt'

def create_lemmas(filename):
    out = {}
    text = open(filename, 'r', encoding='utf-8').read().strip()
    companies = text.split(' # ')
    for comp in companies:
        lemmas = []
        lemms = re.findall('{(.*?)}', comp)
        for lemm in lemms:
            comp = comp.replace('{' + lemm + '}', '')
            lemmas += lemm.replace('?', '').replace('PLUSSS', '+').split('|')
        out[comp.replace('PLUSSS', '+')] = lemmas
    return out

def import_org(org_dic):
    session = db_session()
    for org in org_dic:
        data = {'lemmas' : org_dic[org]}
        new_entity = Entity(name=org, entity_class='organization', data=data)
        session.add(new_entity)
        session.commit()

print('IMPORT ENG')
import_org(create_lemmas(path1))
print('IMPORT RUS')
import_org(create_lemmas(path2))
print('DONE')