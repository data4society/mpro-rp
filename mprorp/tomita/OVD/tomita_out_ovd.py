import re
from mprorp.analyzer.pymystem3_w import Mystem
mystem = Mystem()

def coordinates(fact):
    parameters = {}
    for f in fact['facts']:
        fs = fact['string'].find(f[1].lower())
        if fs == -1:
            print('ERROR : Find = -1 id: ' + str(fact['id']))
            print(str(fact))
        ls = fs + len(f[1]) - 1
        parameters[f[0]] = [fs,ls]
    fact['facts'] = parameters
    return fact

def normalization(fact):
    norm = {}
    wrong = ['край', 'автономная область', 'республика', 'округ', 'область', 'дачный поселок', 'поселок городского типа', 'рабочий поселок', 'город',
             'автономный округ', 'улус', 'район', 'городской округ', 'поселение', 'городской поселок', 'железнодорожный пост', 'железнодорожный разъезд',
             'жилой район', 'аул', 'микрорайон', 'населенный пункт', 'станция', 'село', 'хутор', 'слобода', 'железнодорожная платформа', 'деревня',
             'железнодорожная станция', 'проспект', 'проезд', 'спуск', 'фермерское хозяйство', 'сквер', 'канал', 'дорога', 'квартал', 'платформа', 'переулок',
             'набережная', 'мост', 'аллея', 'шоссе', 'вал', 'проулок', 'площадь', 'переезд', 'ферма', 'тупик', 'парк', 'просек', 'бульвар', 'улица', 'тоннель',
             'просека', 'поселок', 'волость', 'сельский округ', 'сельское поселение', 'курортный поселок', 'станица']
    for f in fact['facts']:
        if f[0] == 'Name' or f[0] == 'Numb':
            norm[f[0]] = [f[1].lower()]
        else:
            normal = ''
            myst = mystem.lemmatize(f[1])
            for el in myst:
                if el != '\n' and el not in wrong:
                    normal += el
            normal = normal.replace('  ', ' ')
            norms = normal.split(' и ')
            norm[f[0]] = norms
    fact['norm'] = norm
    return fact

def get_coordinates(facts, sourse):
    text = open(facts, 'r', encoding='utf-8').read()
    sourse = open(sourse, 'r', encoding='utf-8').read()
    facts = re.findall('<.*?_TOMITA FactID="(\d+?)" .*?pos="(\d+?)" len="(\d+?)" sn="(\d+?)".*?>(.*?)</(\w*?)_TOMITA>', text)
    l = [{'id' : int(i[0]),
          'fs' : int(i[1]),
          'string' : sourse[int(i[1]):int(i[1])+int(i[2])].lower(),
          'facts' : re.findall('<(\w*?)_TOMITA val="(.*?)"/>', i[4]),
          'type' : i[5],
          'sn' : int(i[3]),
          'ls': int(i[1]) + int(i[2])} for i in facts]
    for fact in l:
        fact = normalization(fact)
        fact = coordinates(fact)
        if len(fact['norm']) != len(fact['facts']):
            print('norm != facts')
    return l

def delete_loc(fact_arr):
    all_facts = []
    ovd_coord = []
    loc = []
    for fact in fact_arr:
        if fact['type'][:3] == 'OVD':
            all_facts.append(fact)
            for f in fact['facts']:
                ovd_coord.append([fact['facts'][f][0] + fact['fs'], fact['facts'][f][1] + fact['fs']])
        elif fact['type'] == 'LocationFact':
            loc.append(fact)
        else:
            print('ERROR : Wrong type' + str(fact['id']))
    for fact in loc:
        for f in fact['facts']:
            if good_fact(fact, ovd_coord):
                all_facts.append(fact)
    return all_facts

def good_fact(fact, ovd_coords):
    a = 0
    for f in fact['facts']:
        for ovd_coord in ovd_coords:
            if ovd_coord[1] <= fact['facts'][f][0] + fact['fs']:
                a += 1
            elif fact['facts'][f][1] + fact['fs'] <= ovd_coord[0]:
                a += 1
    if a == len(ovd_coords) * len(fact['facts']):
        return True
    else:
        return False

def sen_division(facts):
    sentences = {}
    for fact in facts:
        if fact['sn'] not in sentences: 
            sentences[fact['sn']] = [fact['id']]
        else:
            sentences[fact['sn']].append(fact['id'])
    return sentences

def pprint():
    a = delete_loc(get_coordinates('facts.xml', 'text_no_n.txt'))
    for i in a:
        print(i)
    print('\n==========\n')
    arr = sen_division(a).keys()
    arr2 = [[] for i in range(min(arr), max(arr) + 1)]
    for i in sen_division(a):
        arr2[i] = sen_division(a)[i]
    print(arr2)