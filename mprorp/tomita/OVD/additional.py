from mprorp.db.models import *
from mprorp.tomita.OVD.city_levenshtein import min_distance, cities


mvd_root = 'eaf0a69a-74d7-4e1a-9187-038a202c7698'


def cross(arr):
    for i in range(len(arr)):
        arr[i] = set(arr[i])
    out = arr[0]
    for i in arr[1:]:
        out = out & i
    return list(out)

def new_cross(arr):
    out = []
    for i in arr[0]:
        for ii in arr[1]:
            if i in ii:
                out.append(ii)
    for i in arr[1]:
        for ii in arr[0]:
            if i in ii:
                out.append(ii)
    out = set(out)
    return list(out)


def Location(loc, session, city, level):
    if len(loc[0]) != 1:
        for i in range(len(loc)):
            loc[i] = loc[i].replace('-', ' ')
            loc[i] = loc[i].split(' ')
    out = []
    for name in loc:
        codes = []
        if len(name) == 1:
            if city is True:
                all_codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(name[0]), KLADR.type == 'Город').all()
            elif level != 0:
                all_codes = session.query(KLADR).filter(KLADR.level == int(level), KLADR.name_lemmas.has_key(name[0])).all()
            else:
                all_codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(name[0])).all()
            for code in all_codes:
                if len(code.name_lemmas) == len(name):
                    codes.append(code)
            out.append(codes)
        else:
            arr = []
            for el in name:
                if city is True:
                    codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(el), KLADR.type == 'Город').all()
                elif level != 0:
                    codes = session.query(KLADR).filter(KLADR.level == int(level), KLADR.name_lemmas.has_key(el)).all()
                else:
                    codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(el)).all()
                arr.append(codes)
            out1 = cross(arr)
            codes = []
            for i in out1:
                codes.append(i)
            out.append(codes)
    return out

def OVD_codes(norms, session):
    out = []
    for fact_name in norms:
        if fact_name == 'Numb':
            out.append(OVD(norms[fact_name], session, Numb=True))
        elif fact_name == 'Name':
            out.append(OVD(norms[fact_name], session, Name=True))
        elif fact_name == 'Location':
            a = OVD(norms[fact_name], session, Location=True)
            if a is not None:
                out.append(a)
        else:
            out.append(OVD(norms[fact_name], session))
    out = cross(out)
    return out

def OVD(ovd, session, Numb=False, Name=False, Location=False):
    codes = []
    if Numb is True:
        numb = ovd[0]
        """
        all_codes = session.query(Entity).filter(Entity.data.has_key("jurisdiction")).all()
        for code in all_codes:
            if code.data["jurisdiction"] == "eaf0a69a-74d7-4e1a-9187-038a202c7698" and numb in code.data['name']:
                codes.append(code)
        """
        codes = session.query(Entity).filter(Entity.data["jurisdiction"].astext == '["'+mvd_root+'"]', Entity.name.like("%"+numb+"%")).all()
    elif Name is True:
        name = ovd[0]
        """
        all_codes = session.query(Entity).filter(Entity.data.has_key("jurisdiction")).all()
        for code in all_codes:
            if code.data["jurisdiction"] == "eaf0a69a-74d7-4e1a-9187-038a202c7698" and name in code.data['name'].lower():
                codes.append(code)
        """
        codes = session.query(Entity).filter(Entity.data["jurisdiction"].astext == '["'+mvd_root+'"]', Entity.name.ilike("%"+name+"%")).all()
    elif Location is True:
        loc = ovd[0].lower()
        levenshtein = min_distance(loc, cities)
        """
        all_codes = session.query(Entity).filter(Entity.data["jurisdiction"].astext == "eaf0a69a-74d7-4e1a-9187-038a202c7698").all()
        for code in all_codes:
            if loc in code.data['name'].lower():
                codes.append(code)
        """
        codes = session.query(Entity).filter(Entity.data["jurisdiction"].astext == '["'+mvd_root+'"]', Entity.name.ilike("%"+loc+"%")).all()
        for city in levenshtein:
            codes += session.query(Entity).filter(Entity.data["jurisdiction"].astext == '["'+mvd_root+'"]', Entity.name.ilike("%"+city+"%")).all()
        if codes == []:
            return None
    else:
        name = ovd[0]
        codes = typess(name, session)
    return codes

def typess(name, session):
    codes = []
    name = name.lower()
    if name != 'овд':
        types = get_types(name)
        """
        all_codes = session.query(Entity).filter(Entity.data.has_key("jurisdiction")).all()
        for code in all_codes:
            for type in types:
                if code.data["jurisdiction"] == "eaf0a69a-74d7-4e1a-9187-038a202c7698" and type in code.name.lower():
                    codes.append(code)
        """
        for type in types:
            codes.extend(session.query(Entity).filter(Entity.data["jurisdiction"].astext == '["' + mvd_root + '"]',
                                         Entity.name.ilike("%" + type + "%")).all())
    else:
        """
        all_codes = session.query(Entity).filter(Entity.data.has_key("jurisdiction")).all()
        for code in all_codes:
            if code.data["jurisdiction"] == "eaf0a69a-74d7-4e1a-9187-038a202c7698":
                codes.append(code)
        """
        codes = session.query(Entity).filter(Entity.data["jurisdiction"].astext == '["' + mvd_root + '"]').all()
    return codes

def get_types(name):
    types = {'_министерство внутренний дело_мвд_' : ['министерство внутренних дел', 'мвд'],
            '_гу мвд_главный управление мвд_':['гу мвд', 'главное управление мвд'],
            '_управление мвд_умвд_':['управление мвд', 'умвд', 'гу мвд'],
            '_межмуниципальный управление_' : ['межмуниципальное управление'],
             '_межмуниципальный отдел_ммо_мо мвд_му мвд_' : ['межмуниципальный отдел', 'ммо', 'мо мвд', 'му мвд'],
             '_линейный управление_лу_управление на транспорт_' : ['линейное управление', 'лу ', 'управление на транспорте'],
             '_линейный отдел_лоп_ло_': ['линейный отдел', 'лоп', 'ло '],
             '_линейный пункт_лпп_' : ['линейный пункт', 'лпп'],
             '_отдел полиция_отделение полиция_оп_омвд_' : ['отдел полиции', 'отделение полиции', 'оп ', 'омвд', 'отдел мвд',
                                                            'отдел министерства внутренних дел'],
             '_пункт полиция_пп_': ['пункт полиции', 'пп']}
    for type in types:
        if '_' + name + '_' in type:
            return types[type]
