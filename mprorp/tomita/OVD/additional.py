from mprorp.db.models import *
def cross(arr):
    for i in range(len(arr)):
        arr[i] = set(arr[i])
    out = arr[0]
    for i in arr[1:]:
        out = out & i
    return out

def Location(loc, session):
    out = []
    for i in range(len(loc)):
        loc[i] = loc[i].replace('-', ' ')
        loc[i] = loc[i].split(' ')
    print(loc)
    for name in loc:
        codes = []
        if len(name) == 1:
            all_codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(name[0])).all()
            for code in all_codes:
                if len(code.name_lemmas) == len(name):
                    codes.append(code)
        else:
            arr = []
            for el in name:
                codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(el)).all()
                arr.append(codes)
            out1 = cross(arr)
            codes = []
            for i in out1:
                codes.append(i)
        out.append(codes)
    return out