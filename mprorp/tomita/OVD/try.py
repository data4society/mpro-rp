from mprorp.tomita.OVD.code_from_db import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *

session = db_session()
fact = {'sn': 17, 'facts': {'Location': [0, 4]}, 'type': 'LocationFact', 'string': 'крыму', 'id': 22, 'fs': 2597,
        'norm': {'City': ['спасск-дальний'],  'Location': ['крым', 'ростов'], 'type_1': ['москва']}}
fact2 = {'string': 'овд «южное медведково', 'sn': 0, 'facts': {'Name': [5, 20], 'OVD': [0, 2]}, 'fs': 129, 'id': 1,
         'norm': {'Name': ['южное медведково'], 'OVD': ['омвд']}, 'type': 'OVDFact'}
#for i in get_codes_for_fact(fact2, session):
#    print(i)
#    for ii in i[0]:
#        print(ii.name)
#a = session.query(KLADR).filter(KLADR.name_lemmas.has_key('крым')).all()