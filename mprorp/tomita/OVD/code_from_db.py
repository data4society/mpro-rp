from mprorp.tomita.OVD.tomita_out_ovd import *
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import itertools

def cross(arr1, arr2):
    out = []
    for i in arr1:
        if i in arr2:
            out.append(i)
    return out


def get_level_of_fact(el):
    el = el[5:]
    levels = el.split('_')
    return levels

def get_codes_for_fact(fact):
    out = []
    fact_type_1 = ['Location']
    fact_type_2 = ['OVD', 'Name', 'Numb']
    fact_type_3 = ['City']
    session = db_session()
    norms = fact['norm']
    for fact_type in norms:
        if fact_type in fact_type_1:
            if len(norms[fact_type]) == 1:
                codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(norms[fact_type][0])).all()
                out.append(codes)
            else:
                codes = []
                for el in norms[fact_type]:
                    codes += session.query(KLADR).filter(KLADR.name_lemmas.has_key(el)).all()
                out.append(codes)
        #elif fact_type in fact_type_2:
            #функция для таблицы с ОВД
        elif fact_type in fact_type_3:
            all_codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(norms[fact_type][0])).all()
            cities = session.query(KLADR).filter_by(fact_type='Город').all()
            codes = cross(all_codes, cities)
            out.append(codes)
        else:
            levels = get_level_of_fact(fact_type)
            all_levels = []
            for level in levels:
                all_levels += session.query(KLADR).filter_by(level=level).all()
            all_els = []
            for el in norms[fact_type]:
                all_els += session.query(KLADR).filter(KLADR.name_lemmas.has_key(el)).all()
            codes = cross(all_levels, all_els)
            out.append(codes)
    return out


def get_all_codes(tomita_out_file, original_text):
    all_facts = delete_loc(get_coordinates(tomita_out_file, original_text))

