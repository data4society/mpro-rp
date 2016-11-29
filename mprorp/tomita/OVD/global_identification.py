from mprorp.tomita.OVD.tomita_out_ovd import sen_division
from mprorp.tomita.OVD.additional import cross
from mprorp.tomita.OVD.code_from_db import get_all_codes
import re

def ovd_combiner(sentences, facts):
    out = []
    for sen_n in sentences:
        ovds = []
        sentence = sentences[sen_n]
        if str(sentence).count('OVD') > 1:
            for fact_id in sentence:
                fact_id = int(re.findall('(\d+?)_', fact_id)[0])
                for fact in facts:
                    if fact['id'] == fact_id and fact['type'] == 'OVDFact':
                        ovds.append(fact)
        else:
            for fact_id in sentence:
                fact_id = int(re.findall('(\d+?)_', fact_id)[0])
                for fact in facts:
                    if fact['id'] == fact_id:
                        out.append(fact)
        if ovds != []:
            for n in range(len(ovds)):
                for m in range(len(ovds)):
                    if ovds[n]['ls'] + 1 == ovds[m]['fs']:
                        new_fact = {'type': 'OVDFact',
                                    'string' : ovds[n]['string'] + ' ' + ovds[m]['string'],
                                    'id' : str(ovds[n]['id']) + str(ovds[m]['id']),
                                    'sn' : ovds[n]['sn'],
                                    'fs' : ovds[n]['fs'],
                                    'ls' : ovds[m]['ls'],
                                    'codes' : cross([ovds[n]['codes'][0], ovds[m]['codes'][0]])}
                        out.append(new_fact)
    return out

def step1(tomita_out_file, original_text):
    facts = get_all_codes(tomita_out_file, original_text)
    sentences = sen_division(facts)
    facts = ovd_combiner(sentences, facts)
    #дописать
    return facts

for i in step1('facts.xml', 'text_no_n.txt'):
    print(i['string'], len(i['codes']))