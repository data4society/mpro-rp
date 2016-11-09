from mprorp.db.models import *

def cross(arr):
    for i in range(len(arr)):
        arr[i] = set(arr[i])
    out = arr[0]
    for i in arr[1:]:
        out = out & i
    return list(out)

def Location(loc, session, city, level):
    for i in range(len(loc)):
        loc[i] = loc[i].replace('-', ' ')
        loc[i] = loc[i].split(' ')
    print(loc)
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
        else:
            out.append(OVD(norms[fact_name], session))
    out = cross(out)
    return out

def OVD(ovd, session, Numb=False, Name=False):
    codes = []
    if Numb is True:
        numb = ovd[0]
        all_codes = session.query(Entity).filter(Entity.data.has_key("org_type")).all()
        for code in all_codes:
            if code.data["org_type"] == 'OVD' and numb in code.data['name']:
                codes.append(code)
    elif Name is True:
        name = ovd[0]
        all_codes = session.query(Entity).filter(Entity.data.has_key("org_type")).all()
        for code in all_codes:
            if code.data["org_type"] == 'OVD' and name in code.data['name'].lower():
                codes.append(code)
    else:
        codes = session.query(Entity).filter(Entity.data.has_key("org_type")).all()
        #дописать про различные типы ОВД
    return codes

