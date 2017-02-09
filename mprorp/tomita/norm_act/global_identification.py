import re
from mprorp.db.models import *
from mprorp.db.dbDriver import *

def act_identification(allacts):
    out = {}
    session = db_session()
    act_db_koap = session.query(Entity).filter(Entity.entity_class == 'norm_act', Entity.name.contains('KOAP')).all()
    act_db_kk = session.query(Entity).filter(Entity.entity_class == 'norm_act', Entity.name.contains('UC')).all()
    for act_str in allacts:
        acts = allacts[act_str]
        acts = acts.split('split')
        if 'KOAP' in str(acts):
            acts = get_codes(act_db_koap, '_k_KOAP_', acts)
        else:
            acts = get_codes(act_db_kk, '_k_KK_', acts)
        out[act_str] = acts
    return out

def get_codes(norm_db, type, acts):
    out = []
    for act in acts:
        if act != type:
            art = re.findall('a_(.*?)_', act)
            if art != []:
                art = art[0]
                if art[-1] != '.':
                    art = art + '.'
                if 'p' in act:
                    parts = re.findall('p_(.*?)_', act)
                    for n in range(len(parts)):
                        if parts[n][-1] != '.':
                            parts[n] = parts[n] + '.'
                    for norm in norm_db:
                        if norm.data['art'] == art:
                            if 'part' in norm.data and norm.data['part'] in parts:
                                out.append(norm)
                else:
                    if type == '_k_KK_':
                        art = art[:-1]
                    for norm in norm_db:
                        if norm.data['art'] == art and 'part' not in norm.data:
                            out.append(norm)
    return out