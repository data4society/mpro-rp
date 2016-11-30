from mprorp.tomita.OVD.tomita_out_ovd import sen_division
from mprorp.tomita.OVD.additional import cross
from mprorp.tomita.OVD.code_from_db import get_all_codes
import re

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
                cross_codes = cross([fact1['codes'][0], fact2['codes'][0]])
                if cross_codes != []:
                    new_fact = {'type': fact_type,
                                'string' : fact1['string'] + ' ' + fact2['string'],
                                'id' : str(fact1['id']) + str(fact2['id']),
                                'sn' : fact1['sn'],
                                'fs' : fact1['fs'],
                                'ls' : fact2['ls'],
                                'codes' : cross_codes}
                    out.append(new_fact)
                    used.append(fact1)
                    used.append(fact2)
        if fact1 not in used:
            fact1['codes'] = fact1['codes'][0]
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
                                         'code' : ovd_code.external_data['kladr']},
                                              'weight' : 1/(max(loc['ls'], ovd['ls']) - min(loc['fs'], ovd['fs']))}]
                        else:
                            out[ovd['id']].append({'fact' : {'type' : 'OVDVariant',
                                         'string' : ovd['string'],
                                         'fs' : ovd['fs'],
                                         'ls' : ovd['ls'],
                                         'loc_used' : loc['string'],
                                         'code' : ovd_code.external_data['kladr']},
                                              'weight' : 1/(max(loc['ls'], ovd['ls']) - min(loc['fs'], ovd['fs']))})
                        used.append(ovd)
        if ovd not in used:
            out[ovd['id']] = {'weight' : 100000, 'fact' : ovd}
    return out

def step1(tomita_out_file, original_text):
    facts = get_all_codes(tomita_out_file, original_text)
    facts = combiner(facts, 'OVDFact')
    facts = combiner(facts, 'LocationFact')
    sentences = sen_division(facts)
    out = variants(facts)
    print('sentences: ' + str(sentences) + '\n')
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