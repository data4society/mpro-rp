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
    for n in range(len(text)):
        if 'TOMITA =' in text[n]:
            fact = re.findall('TOMITA = (.*)', text[n])[0]
            name_fact = re.findall('(.*)_TOMITA', text[n])[0]
            print(fact)
            first_symbol = sourse.find(fact)
            fact = re.sub(' ,', ',', fact)
            if first_symbol != -1:
                last_symbol = first_symbol + len(fact)
                symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
            else:
                print('change')
                fact_new = re.sub(' ', '', fact)
                first_symbol = sourse.find(fact_new)
                if first_symbol == -1:
                    fact = re.sub('"(\w*)"?', '«\\1»', fact)
                    first_symbol = sourse.find(fact)
                    last_symbol = first_symbol + len(fact)
                    symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)
                else:
                    fact = fact_new
                    last_symbol = first_symbol + len(fact)
                    symbols = str(first_symbol + len_of_line) + ':' + str(last_symbol + len_of_line)

            #print(fact)
            #print(symbols)
            #print(sourse[first_symbol:last_symbol])
            #print(s[first_symbol + len_of_line:last_symbol + len_of_line])
            # print(sourse)

            out[symbols] = name_fact
            sourse = sourse[last_symbol:]
            len_of_line += last_symbol
    return out


def tomita_out(file_name, source_name):
    out = list_make(text_make(file_name), source_name)
    return out