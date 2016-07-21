import re


def text_make(file_name):
    text = []
    f = open(file_name, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        text.append(line)
    return text


def list_make(text, source_name):
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
            fact = re.sub('"', '', fact)
            #print('fact changed: ' + fact)
            first_symbol = sourse.find(fact)
            if first_symbol != -1:
                last_symbol = first_symbol + len(fact)
                symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
            else:
                #print('change1')
                fact = re.sub('\\. ', '.', fact)
                first_symbol = sourse.find(fact)
                if first_symbol != -1:
                    last_symbol = first_symbol + len(fact)
                    symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
                else:
                    #print('change2')
                    fact = re.sub(' ', '', fact)
                    first_symbol = sourse.find(fact)
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

def tomita_out(file_name, source_name):
    out = list_make(text_make(file_name), source_name)
    return out

