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
                        out.append(({'type' : 'OVDVariant',
                                         'string' : ovd['string'],
                                         'fs' : ovd['fs'],
                                         'ls' : ovd['ls'],
                                         'loc_used' : loc['string'],
                                         'codes' : [ovd_code]},
                                     1 / (max(loc['fs'], ovd['fs']) - min(loc['ls'], ovd['ls']))))
                        used.append(ovd)
        if ovd not in used:
            out.append((ovd, 0))
    return out


def step1(tomita_out_file, original_text, n):
    facts = get_all_codes(tomita_out_file, original_text)
    for fact in facts:
        fact['codes'] = codes_to_norm(fact)
    facts = combiner(facts, 'OVDFact')
    facts = combiner(facts, 'LocationFact')
    facts = variants(facts)
    out = step2(facts)
    print(out)
    out = max_amount_of_codes(out, n)
    out = step3(out)
    out = step4(out)
    return out

def step2(facts):
    out_all = []
    out = []
    max_weight = 0
    fs1 = -1
    for fact in facts:
        fs = fact[0]['fs']
        if fs == fs1:
            if fact[1] > max_weight:
                max_weight = fact[1]
                out = [fact]
            elif fact[1] == max_weight:
                out.append(fact)
        else:
            if out != []:
                out_all.append(out)
            fs1 = fs
            max_weight = 0
            if fact[1] > max_weight:
                max_weight = fact[1]
                out = [fact]
            elif fact[1] == max_weight:
                out.append(fact)
    out_all.append(out)
    return out_all

def step3(arr):
    out = {}
    for facts in arr:
        for fact in facts:
            idd = str(fact[0]['fs']) + ':' + str(fact[0]['ls'])
            if idd not in out:
                out[idd] = fact[0]['codes']
            else:
                out[idd] += fact[0]['codes']
    return out

def step4(facts):
    session = db_session()
    out = {}
    for fact in facts:
        codes = facts[fact]
        if len(codes) == 1:
            out2 = []
            for code in codes:
                idd = str(session.query(Entity).filter(Entity.external_data['kladr'].astext == code).first().entity_id).replace("UUID('", '').replace("')", '')
                out2.append(idd)
            if out2 != []:
                out[fact] = out2[0]
    return out

def max_amount_of_codes(facts, n):
    out = []
    for fact in facts:
        if 0 < len(fact) <= n:
            out.append(fact)
    return out

def cut_kladr(code):
    if len(code) > 12:
        r1 = code[0:3]
        r2 = code[3:6]
        c = code[6:9]
        p = code[9:13]
        other = code[13:]
        parts = ((r1,r1+r2+c+p+other), (r2,r2+c+p+other), (c,c+p+other), (p,p+other), (other,other))
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
