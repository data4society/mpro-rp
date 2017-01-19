from mprorp.tomita.OVD.tomita_out_ovd import sen_division
from mprorp.analyzer.db import *
from mprorp.tomita.OVD.additional import cross, new_cross
from mprorp.tomita.OVD.code_from_db import get_all_codes
import re

def codes_to_norm(fact):
    codes = fact['codes']
    out = []
    if codes != []:
        for code in codes:
            level = str(code).count('[')
            for n in range(level - 1):
                code = code[0]
            out += code
        for n in range(len(out)):
            if fact['type'] == 'OVDFact':
                out[n] = out[n].external_data['kladr']
            else:
                out[n] = cut_kladr(out[n].kladr_id)
        return out
    else:
        return codes

def loc_to_ovd(ovd, loc):
    if loc in ovd:
        return True
    else:
        if len(loc) > 12:
            loc = cut_kladr(loc[0:11])
            if loc in ovd:
                return True
            else:
                return False
        else:
            return False

def combiner(facts, fact_type):
    if fact_type == 'OVDFact':
        n = 2
    else:
        n = 5
    out = []
    used = []
    ovds = []
    for fact in facts:
        if fact['type'] == fact_type:
            ovds.append(fact)
        else:
            out.append(fact)
    for fact1 in ovds:
        for fact2 in ovds:
            if 0 < fact2['fs'] - fact1['ls'] < n:
                if fact_type == 'OVDFact':
                    cross_codes = cross([fact1['codes'], fact2['codes']])
                else:
                    cross_codes = new_cross([fact1['codes'], fact2['codes']])
                if cross_codes != []:
                    new_fact = {'type': fact_type,
                                'string' : fact1['string'] + ' ' + fact2['string'],
                                'id' : str(fact1['id']) + '_' +  str(fact2['id']),
                                'sn' : fact1['sn'],
                                'fs' : fact1['fs'],
                                'ls' : fact2['ls'],
                                'codes' : cross_codes}
                    out.append(new_fact)
                    used.append(fact1)
                    used.append(fact2)
    for fact in ovds:
        if fact not in used:
            out.append(fact)
    return out

def variants(facts):
    ovds = []
    locs = []
    out = []
    used = []
    for fact in facts:
        if fact['type'] == 'OVDFact':
            ovds.append(fact)
        else:
            locs.append(fact)
    for ovd in ovds:
        for loc in locs:
            for ovd_code in ovd['codes']:
                for loc_code in loc['codes']:
                    if loc_to_ovd(ovd_code, loc_code) is True:
                        try:
                            out.append(({'type' : 'OVDVariant',
                                             'string' : ovd['string'],
                                             'fs' : ovd['fs'],
                                             'ls' : ovd['ls'],
                                             'loc_used' : loc['string'],
                                             'loc_used_norm' : loc['norm'][[i for i in loc['norm']][0]][0][0],
                                             'codes' : [ovd_code]},
                                         1 / (max(loc['fs'], ovd['fs']) - min(loc['ls'], ovd['ls']))))
                            used.append(ovd)
                        except:
                            out.append(({'type': 'OVDVariant',
                                         'string': ovd['string'],
                                         'fs': ovd['fs'],
                                         'ls': ovd['ls'],
                                         'loc_used': loc['string'],
                                         'codes': [ovd_code]},
                                        1 / (max(loc['fs'], ovd['fs']) - min(loc['ls'], ovd['ls']))))
                            used.append(ovd)
        if ovd not in used:
            out.append((ovd, 0))
    return out


def step1(tomita_out_file, original_text, n):
    session = db_session()
    facts = get_all_codes(tomita_out_file, original_text)
    for fact in facts:
        fact['codes'] = codes_to_norm(fact)
    facts = del_countries(facts)
    print(facts)
    facts = combiner(facts, 'OVDFact')
    facts = combiner(facts, 'LocationFact')
    facts = variants(facts)
    facts = skleyka(facts)
    print(facts)
    out = step2(facts)
    print(out)
    out = max_amount_of_codes(out, n)
    print(out)
    out = choose_nearest(out)
    print(out)
    out = step3(out)
    print(out)
    out = step4(out, session)
    return out

def step2(facts):
    out = []
    fs1 = -1
    new_ovd = []
    for fact in facts:
        fs = fact[0]['fs']
        if fs != fs1:
            fs1 = fs
            if new_ovd != []:
                out.append(new_ovd)
            new_ovd = [fact]
        else:
            new_ovd.append(fact)
    out.append(new_ovd)
    return out

def step3(facts):
    out = {}
    for fact in facts:
        idd = str(fact[0]['fs']) + ':' + str(fact[0]['ls'])
        if idd not in out:
            out[idd] = fact[0]['codes']
        else:
            out[idd] += fact[0]['codes']
    return out

def step4(facts, session):
    out = {}
    for fact in facts:
        codes = list(set(facts[fact]))
        if len(codes) == 1:
            out2 = []
            for code in codes:
                idd = str(session.query(Entity).filter(Entity.external_data['kladr'].astext == code).first().entity_id).replace("UUID('", '').replace("')", '')
                out2.append(idd)
            if out2 != []:
                out[fact] = out2[0]
    return out

def max_amount_of_codes(facts, n):
    out2 = []
    for ovd in facts:
        out = []
        loc_used = []
        loc = ''
        for variant in ovd:
            try:
                if variant[0]['loc_used'] != loc:
                    if loc_used != []:
                        out.append(loc_used)
                    loc = variant[0]['loc_used']
                    loc_used = [variant]
                else:
                    loc_used.append(variant)
            except:
                out.append([variant])
        out.append(loc_used)
    out2.append(out)
    out = []
    for ovd in out2:
        for var in ovd:
            if len(var) <= n:
                out.append(var)
    return out

def choose_nearest(facts):
    out = []
    for ovd in facts:
        weight = -10000
        for loc in ovd:
            if loc[1] > weight:
                weight = loc[1]
                best = loc
        out.append(best)
    return out


def cut_kladr(code):
    if len(code) > 12:
        r1 = code[0:3]
        r2 = code[3:6]
        c = code[6:9]
        p = code[9:13]
        other = code[13:]
    else:
        r1 = code[0:3]
        r2 = code[3:6]
        c = code[6:9]
        p = code[9:len(code)]
        other = ''
    parts = ((r1,r1+r2+c+p+other), (r2,r2+c+p+other), (c,c+p+other), (p,p+other), (other,other))
    kladr = ''
    for part in parts:
        if part[1].count('0') != len(part[1]):
            kladr += part[0]
        else:
            return kladr
    return kladr

def del_countries(facts):
    out = []
    countries = ['казахстан']
    for fact in facts:
        if fact['type'] == 'LocationFact':
            try:
                loc = fact['norm'][[i for i in fact['norm']][0]][0][0]
                if loc not in countries:
                    out.append(fact)
            except:
                continue
        else:
            out.append(fact)
    return out

def skleyka(facts):
    out = []
    for fact in facts:
        if fact not in out:
            out.append(fact)
    return out

def loc_in_name(out, session):
    out2 = []
    for ovd in out:
        new_out = []
        for el in ovd:
            ovd_name = session.query(Entity).filter(Entity.external_data['kladr'].astext == el[0]['codes'][0]).first().name
            try:
                if el[0]['loc_used'][:-1] in ovd_name.lower() or el[0]['loc_used_norm'][:-1] in ovd_name.lower():
                    new_out.append(el)
            except:
                continue
        if new_out == []:
            out2.append(ovd)
        else:
            out2.append(new_out)
    return out2
