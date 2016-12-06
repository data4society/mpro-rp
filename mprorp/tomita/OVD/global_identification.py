from mprorp.tomita.OVD.tomita_out_ovd import sen_division
from mprorp.tomita.OVD.additional import cross
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
        return out
    else:
        return codes


def combiner(facts, fact_type):
    if fact_type == 'OVDFact':
        n = 2
    else:
        n = 100
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
                cross_codes = cross([fact1['codes'], fact2['codes']])
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
        if fact1 not in used:
            out.append(fact1)
    return out

def variants(facts):
    out = {}
    ovds = []
    locs =[]
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
                    if loc_code.kladr_id[:-1] in ovd_code.external_data['kladr']:
                        if ovd['id'] not in out:
                            out[ovd['id']] = [{'fact' : {'type' : 'OVDVariant',
                                         'string' : ovd['string'],
                                         'fs' : ovd['fs'],
                                         'ls' : ovd['ls'],
                                         'loc_used' : loc['string'],
                                         'codes' : [str(ovd_code.entity_id).replace("UUID('", '').replace("')", '')]},
                                              'weight' : 1/(max(loc['ls'], ovd['ls']) - min(loc['fs'], ovd['fs']))}]
                        else:
                            out[ovd['id']].append({'fact' : {'type' : 'OVDVariant',
                                         'string' : ovd['string'],
                                         'fs' : ovd['fs'],
                                         'ls' : ovd['ls'],
                                         'loc_used' : loc['string'],
                                         'codes' : [str(ovd_code.entity_id).replace("UUID('", '').replace("')", '')]},
                                              'weight' : 1/(max(loc['ls'], ovd['ls']) - min(loc['fs'], ovd['fs']))})
                        used.append(ovd)
        if ovd not in used:
            codes = []
            for code in ovd['codes']:
                codes.append(str(code.entity_id).replace("UUID('", '').replace("')", ''))
            ovd['codes'] = codes
            if len(codes) < 4:
                out[ovd['id']] = [{'weight' : 1, 'fact' : ovd}]
            else:
                out[ovd['id']] = [{'weight': 0, 'fact': ovd}]
    return out

def step1(tomita_out_file, original_text, n):
    facts = get_all_codes(tomita_out_file, original_text)
    for fact in facts:
        fact['codes'] = codes_to_norm(fact)
    facts = combiner(facts, 'OVDFact')
    facts = combiner(facts, 'LocationFact')
    out = variants(facts)
    out = step2(out)
    out = max_amount_of_codes(out, n)
    #print('sentences: ' + str(sen_division(facts)) + '\n')
    return out

def step2(variantss):
    max_facts = {}
    for idd in variantss:
        max_weight = 0
        for fact in variantss[idd]:
            if fact['weight'] > max_weight:
                max_weight = fact['weight']
        for fact in variantss[idd]:
            if fact['weight'] == max_weight and len(fact['fact']['codes']) < 4:
                if str(fact['fact']['fs']) + ':' + str(fact['fact']['ls']) not in max_facts:
                    max_facts[str(fact['fact']['fs']) + ':' + str(fact['fact']['ls'])] = fact['fact']['codes']
                else:
                    max_facts[str(fact['fact']['fs']) + ':' + str(fact['fact']['ls'])] += fact['fact']['codes']
    return max_facts

def max_amount_of_codes(codes, n):
    out = {}
    for coord in codes:
        if 0 < len(codes[coord]) <= n:
            if n == 1:
                out[coord] = codes[coord][0]
            else:
                out[coord] = codes[coord]
    return out


def pprint():
    f = open('text_no_n.txt', 'r', encoding='utf-8').read()
    print('original text: ' + f)
    out = step1('facts.xml', 'text_no_n.txt')
    for i in out:
        print('id: ' + str(i))
        for ii in out[i]:
            print('weight: ' + str(ii['weight']))
            print('ovd: ' + str(ii['fact']))
            print('original string: ' + f[ii['fact']['fs']:ii['fact']['ls']])
            print('\n')