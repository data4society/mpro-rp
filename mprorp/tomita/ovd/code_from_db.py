from mprorp.tomita.ovd.tomita_out_ovd import *
from mprorp.db.dbDriver import *
from mprorp.tomita.ovd.additional import *


def get_level_of_fact(el):
    el = el[5:]
    levels = el.split('_')
    return levels

def get_codes_for_fact(fact, session):
    out = []
    norms = fact['norm']
    if 'OVD' not in norms:
        for fact_type in norms:
            if fact_type == 'Location':
                codes = Location(norms[fact_type], session, city=False, level=0)
                out.append(codes)
            elif fact_type == 'City':
                codes = Location(norms[fact_type], session, city=True, level=0)
                out.append(codes)
            else:
                codes = []
                levels = get_level_of_fact(fact_type)
                for l in levels:
                    codes += Location(norms[fact_type], session, city=False, level=int(l))
                out.append(codes)

    else:
        codes = OVD_codes(norms, session)
        out.append([codes])
    return out


def get_all_codes(tomita_out_file, original_text, tomita_path):
    out = []
    session = db_session()
    all_facts = delete_loc(get_coordinates(tomita_out_file, original_text, tomita_path))
    for fact in all_facts:
        if "'norm': {'Location': ['россия']}" not in str(fact):
            fact['codes'] = get_codes_for_fact(fact, session)[0]
            out.append(fact)
    return out