import re
from mprorp.controller.init import global_mystem as mystem

def normalization(fact):
    norm = ''
    for n in mystem.lemmatize(fact['string']):
        if n != '\n':
            norm += n
    fact['norm'] = norm
    return fact

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


def get_coordinates(facts, sourse, tomita_path):
    text = open(tomita_path + '/' + facts, 'r', encoding='utf-8').read()
    sourse = open(tomita_path + '/' + sourse, 'r', encoding='utf-8').read()
    facts = re.findall('<.*?_TOMITA FactID="(\d+?)" .*?pos="(\d+?)" len="(\d+?)" sn="(\d+?)".*?>(.*?)</([A-z]*?)_TOMITA>', text)
    l = [{'id': int(i[0]),
          'fs': int(i[1]),
          'string': sourse[int(i[1]):int(i[1])+int(i[2])].lower(),
          'facts': re.findall('<(.*?)_TOMITA val="(.*?)" pos', i[4]),
          'type': i[5],
          'sn': int(i[3]),
          'ls': int(i[1]) + int(i[2])} for i in facts if sourse[int(i[1]) - 1] not in ['"', '«']
         and sourse[int(i[1]) + int(i[2]) + 1] not in ['"', '»']]
    for n in range(len(l)):
        l[n] = coordinates(l[n])
        l[n] = normalization(l[n])
    return l