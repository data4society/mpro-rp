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


def list_make(text, source_name):
    """function to create dictionary with coordinates"""
    sourse = open(source_name, 'r', encoding='utf-8').read()
    #s = sourse
    sourse = re.sub('\n', ' ', sourse)
    out = {}
    len_of_line = 0
    #ERROR = 0
    for n in range(len(text)):
        if 'TOMITA =' in text[n]:
            fact = re.findall('TOMITA = (.*)', text[n])[0]
            name_fact = re.findall('(.*)_TOMITA', text[n])[0]
            #print('fact detected: ' + fact)
            fact = re.sub(' ,', ',', fact)
            fact = re.sub('«', '', fact)
            fact = re.sub('»', '', fact)
            fact1 = re.sub('"', '', fact)
            fact2 = re.sub('\\. ', '.', fact)
            first_symbol1 = sourse.find(fact1)
            first_symbol2 = sourse.find(fact2)
            #print('fact1 : ' + fact1 + ' ' + str(first_symbol1))
            #print('fact2 : ' + fact2 + ' ' + str(first_symbol2))
            if first_symbol1 == -1 and first_symbol2 == -1:
                #print('change', file=stream)
                fact = re.sub(' ', '', fact)
                #print('fact changed: ' + fact)
                first_symbol = sourse.find(fact)
                last_symbol = first_symbol + len(fact)
                symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
            if first_symbol1 == -1:
                first_symbol = first_symbol2
                fact = fact2
                last_symbol = first_symbol + len(fact)
                symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
            if first_symbol2 == -1:
                first_symbol = first_symbol1
                fact = fact1
                last_symbol = first_symbol + len(fact)
                symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
            if first_symbol1 != -1 and first_symbol2 != -1:
                first_symbol = min(first_symbol1, first_symbol2)
                if first_symbol == first_symbol1:
                    fact = fact1
                if first_symbol == first_symbol2:
                    fact = fact2
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

def find_act(file_name):
    string = open(file_name, 'r', encoding='utf-8').read()
    numb = '(\d+|[\d\.]+)'

    part = '((ч.|част\w*) ?'+numb+')'
    parts = '(' + part + '.*)'

    article = '((ст.|стать\w*) ?'+numb+')'
    articles = '(' + article + '.*)'

    paragraph = '((п.|пункт\w*) ?'+numb+')'
    paragraphs = '(' + paragraph + '.*)'

    KK = '(УК|КоАП|КОАП|[Уу]головн.* [Кк]одекс.? \w*)'
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

def norm_out(arr, source_name):
    source = open(source_name, 'r', encoding='utf-8').read()
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

def tomita_out(file_name, source_name):
    """function to run all together"""
    out = list_make(text_make(file_name), source_name)
    return out

