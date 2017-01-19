"""function to create dictionary with coordinates of facts in text"""
import re


def text_make(file_name):
    """function to create array with text lines"""
    text = []
    f = open(file_name, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        text.append(line)
    return text

def facts(fact, sourse):
    fs = []
    facts = []
    fact1 = re.sub('"', '', fact)
    f1 = sourse.find(fact1)
    if f1 != -1:
        fs.append(f1)
        facts.append(fact1)
    fact2 = re.sub('\\. (\w)\\.', '.\\1.', fact)
    f2 = sourse.find(fact2)
    if f2 != -1:
        fs.append(f2)
        facts.append(fact2)
    fact3 = re.sub('\\. ', '.', fact)
    f3 = sourse.find(fact3)
    if f3 != -1:
        fs.append(f3)
        facts.append(fact3)
    fact4 = re.sub(' ', '', fact)
    f4 = sourse.find(fact4)
    if f4 != -1:
        fs.append(f4)
        facts.append(fact4)
    fact5 = re.sub('a', 'а', fact)
    fact5 = re.sub('і', 'i', fact5)
    fact5 = re.sub('І', 'I', fact5)
    f5 = sourse.find(fact5)
    if f5 != -1:
        fs.append(f5)
        facts.append(fact5)
    if fs != []:
        first_symbol = min(fs)
        fact = facts[fs.index(first_symbol)]
    else:
        first_symbol = 0
    return fact, first_symbol


def list_make(text, source_name, tomita_path):
    """function to create dictionary with coordinates"""
    sourse = open(tomita_path + '/' + source_name, 'r', encoding='utf-8').read()
    #s = sourse
    sourse = re.sub('\n', ' ', sourse)
    out = {}
    len_of_line = 0
    #ERROR = 0
    for n in range(len(text)):
        if 'TOMITA =' in text[n]:
            fact = re.findall('TOMITA = (.*)', text[n])[0]
            name_fact = re.findall('(.*)_TOMITA', text[n])[0]
            fact = re.sub(' ,', ',', fact)
            fact = re.sub('«', '', fact)
            fact = re.sub('»', '', fact)
            fact, first_symbol = facts(fact, sourse)
            last_symbol = first_symbol + len(fact)
            symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)

            #print(sourse[:20])
            #print('the last version of fact: ' + fact)
            #print('symbols: ' + symbols)
            #print('string now in original text: + 'sourse[first_symbol:last_symbol])
            #print('string in original text: ' + s[first_symbol + len_of_line:last_symbol + len_of_line])
            #if fact != s[first_symbol + len_of_line:last_symbol + len_of_line]:
                #print('ERROR', file=stream)
                #ERROR += 1
            #print('\n')

            out[symbols] = name_fact
            sourse = sourse[last_symbol:]
            len_of_line += last_symbol

    #print('Error count = ' + str(ERROR) + '\n')
    return out

def find_act(file_name, tomita_path):
    string = open(tomita_path + '/' + file_name, 'r', encoding='utf-8').read()
    numb = '(\d+|[\d\.]+)'

    part = '((ч\.|част[а-я]*) ?' + numb + ')'
    parts = '(' + part + '.*?)'

    article = '((ст\.|стать[а-я]*) ?' + numb + ')'
    articles = '(' + article + '.*?)'

    paragraph = '((п\.|пункт[а-я]*) ?' + numb + ')'
    paragraphs = '(' + paragraph + '.*?)'

    KK = '(УК\W|КоАП|УПК|КОАП|[Уу]головн\w*? [Кк]одекс.? [А-я ]*)'
    string = re.sub(KK, '\\1@#@', string)
    strings = string.split('@#@')

    norm_act1 = '(' + parts + '*' + articles + '*' + paragraphs + '*' + KK + ')'
    norm_act2 = '(' + parts + '*' + paragraphs + '*' + articles + '*' + KK + ')'
    norm_act3 = '(' + articles + '*' + parts + '*' + paragraphs + '*' + KK + ')'
    norm_act4 = '(' + articles + '*' + paragraphs + '*' + parts + '*' + KK + ')'
    norm_act5 = '(' + paragraphs + '*' + articles + '*' + parts + '*' + KK + ')'
    norm_act6 = '(' + paragraphs + '*' + parts + '*' + articles + '*' + KK + ')'

    norm_act_all = '(' + norm_act1 + '|' + norm_act2 + '|' + norm_act3 + '|' + norm_act4 + '|' + norm_act5 + '|' + norm_act6 + ')'

    out = []
    for line in strings:
        norm_act = re.findall(norm_act_all, line)
        if norm_act != []:
            norm_act = norm_act[0]
            if norm_act != '':
                out.append(max(norm_act))
    return out

def norm_out(arr, source_name, tomita_path):
    source = open(tomita_path + '/' + source_name, 'r', encoding='utf-8').read()
    s = source
    out = {}
    len_of_line = 0
    for act in arr:
        first_symbol = source.find(act)
        last_symbol = first_symbol + len(act)
        symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
        #print('string in original text: ' + s[first_symbol + len_of_line:last_symbol + len_of_line])
        out[symbols] = 'Norm'
        source = source[last_symbol:]
        len_of_line += last_symbol
    return out

def tomita_out(file_name, source_name, tomita_path):
    """function to run all together"""
    out = list_make(text_make(tomita_path + '/' + file_name), source_name, tomita_path)
    return out

