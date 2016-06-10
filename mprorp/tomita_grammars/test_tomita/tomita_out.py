import re

def text_make(file_name):
    text = []
    f = open(file_name, 'r', encoding='utf-8')
    for line in f:
        line = line.strip()
        text.append(line)
    return text


def list_make(text):
    out = {}
    len_of_line = 0
    for n in range(len(text)):
        if '_TOMITA' not in text[n]:
            if text[n] != '{':
                if text[n] != '}':
                    line = text[n][:-2]
        if 'TOMITA =' in text[n]:
            fact = re.findall('TOMITA = (.*)', text[n])[0]
            name_fact = re.findall('(.*)_TOMITA', text[n])[0]
            while fact in line:
                first_symbol = line.find(fact)
                last_symbol = first_symbol + len(fact)
                symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
                out[symbols] = name_fact
                line = line[last_symbol:]
            len_of_line += len(text[n])
    return out

def tomita_out(file_name):
    out = list_make(text_make(file_name))
    return out


