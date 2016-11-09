from mprorp.tomita.OVD.tomita_out_ovd import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.tomita.OVD.additional import *
import itertools


def get_level_of_fact(el):
    el = el[5:]
    levels = el.split('_')
    return levels

def get_codes_for_fact(fact, session):
    out = []
    fact_type_1 = ['Location']
    fact_type_2 = ['OVD', 'Name', 'Numb']
    fact_type_3 = ['City']
    norms = fact['norm']
    for fact_type in norms:
        if fact_type in fact_type_1:
            out = Location(norms[fact_type], session)
        elif fact_type in fact_type_2:
            out.append([])
            #функция для таблицы с ОВД
        elif fact_type in fact_type_3:
            codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(norms[fact_type][0]), KLADR.fact_type == 'Город').all()
            out.append(codes)
        else:
            codes = []
            levels = get_level_of_fact(fact_type)
            for l in levels:
                for el in norms[fact_type]:
                    codes += session.query(KLADR).filter(KLADR.level == int(l), KLADR.name_lemmas.has_key(el)).all()
            out.append(codes)
    return out


def get_all_codes(tomita_out_file, original_text):
    session = db_session()
    all_facts = delete_loc(get_coordinates(tomita_out_file, original_text))
    for fact in all_facts:
        fact['codes'] = get_codes_for_fact(fact, session)
    return all_facts

#a = get_all_codes('facts.xml', 'text.txt')
#for i in a:
#    print([len(ii) for ii in i['codes']])