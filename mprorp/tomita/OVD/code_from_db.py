from mprorp.tomita.OVD.tomita_out_ovd import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *

def get_level_of_fact(el):
    el = el[5:]
    levels = el.split('_')
    return levels

def get_codes_for_fact(fact):
    type_1 = ['Location']
    type_2 = ['OVD', 'Name', 'Numb']
    type_3 = ['Str']
    session = db_session()
    norms = fact['norm']
    for type in norms:
        if type in type_1:
            all_codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(norms[type])).all()
        elif type in type_2:
        elif type in type_3:
            all_codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(norms[type])).all()
            street = session.query(KLADR).filter_by(type=).all()
        else:
            levels = get_level_of_fact(type)



def get_all_codes(tomita_out_file, original_text):
    all_facts = delete_loc(get_coordinates(tomita_out_file, original_text))

