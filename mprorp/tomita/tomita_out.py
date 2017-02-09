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
    #string = '''Статья 30. Порядок предоставления земельных участков для строительства из земель, находящихся в государственной или муниципальной собственности
#
#1. Предоставление земельных участков для строительства из земель, находящихся в государственной или муниципальной собственности, осуществляется с проведением работ по их формированию: 1) без предварительного согласования мест размещения объектов; 2) с предварительным согласованием мест размещения объектов.
#
#2. Предоставление земельных участков для строительства в собственность без предварительного согласования мест размещения объектов осуществляется исключительно на торгах (конкурсах, аукционах) в соответствии со статьей 38 настоящего Кодекса.
#
#3. Предоставление земельных участков для строительства с предварительным согласованием мест размещения объектов осуществляется в аренду, а лицам, указанным в пункте 1 статьи 20 настоящего Кодекса, в постоянное (бессрочное) пользование.
#
#4. Предоставление земельного участка для строительства без предварительного согласования места размещения объекта осуществляется в следующем порядке: 1) проведение работ по формированию земельного участка: подготовка проекта границ земельного участка и установление его границ на местности; определение разрешенного использования земельного участка; определение технических условий подключения объектов к сетям инженерно-технического обеспечения; принятие решения о проведении торгов (конкурсов, аукционов) или предоставлении земельных участков без проведения торгов (конкурсов, аукционов); публикация сообщения о проведении торгов (конкурсов, аукционов) или приеме заявлений о предоставлении земельных участков без проведения торгов (конкурсов, аукционов); 2) государственный кадастровый учет земельного участка в соответствии с правилами, предусмотренными статьей 70 настоящего Кодекса; 3) проведение торгов (конкурсов, аукционов) по продаже земельного участка или продаже права на заключение договора аренды земельного участка или предоставление земельного участка в аренду без проведения торгов (конкурсов, аукционов) на основании заявления гражданина или юридического лица, заинтересованных в предоставлении земельного участка. Передача земельных участков в аренду без проведения торгов (конкурсов, аукционов) допускается при условии предварительной и заблаговременной публикации сообщения о наличии предлагаемых для такой передачи земельных участков в случае, если имеется только одна заявка; 4) подписание протокола о результатах торгов (конкурсов, аукционов) или подписание договора аренды земельного участка в результате предоставления земельного участка без проведения торгов (конкурсов, аукционов).
#
#5. Предоставление земельного участка для строительства с предварительным согласованием места размещения объекта осуществляется в следующем порядке: 1) выбор земельного участка и принятие в порядке, установленном статьей 31 настоящего Кодекса, решения о предварительном согласовании места размещения объекта; 2) проведение работ по формированию земельного участка; 3) государственный кадастровый учет земельного участка в соответствии с правилами, предусмотренными статьей 70 настоящего Кодекса; 4) принятие решения о предоставлении земельного участка для строительства в соответствии с правилами, установленными статьей 32 настоящего Кодекса.
#
#6. В случае, если земельный участок сформирован, но не закреплен за гражданином или юридическим лицом, его предоставление для строительства осуществляется в соответствии с подпунктами 3 и 4 пункта 4 настоящей статьи.
#
#7. Решение исполнительного органа государственной власти или органа местного самоуправления, предусмотренных статьей 29 настоящего Кодекса, о предоставлении земельного участка для строительства или протокол о результатах торгов (конкурсов, аукционов) является основанием: 1) государственной регистрации права постоянного (бессрочного) пользования при предоставлении земельного участка в постоянное (бессрочное) пользование; 2) заключения договора купли-продажи и государственной регистрации права собственности покупателя на земельный участок при предоставлении земельного участка в собственность; 3) заключения договора аренды земельного участка и государственной регистрации данного договора при передаче земельного участка в аренду.
#
#8. Решение или выписка из него о предоставлении земельного участка для строительства либо об отказе в его предоставлении выдается заявителю в семидневный срок со дня его принятия.
#
#9. Решение об отказе в предоставлении земельного участка для строительства может быть обжаловано заявителем в суд.
#
#10. В случае признания судом недействительным отказа в предоставлении земельного участка для строительства суд в своем решении обязывает исполнительный орган государственной власти или орган местного самоуправления, предусмотренные статьей 29 настоящего Кодекса, предоставить земельный участок с указанием срока и условий его предоставления.
#
#11. Предварительное согласование места размещения объекта не проводится при размещении объекта в городском или сельском поселении в соответствии с градостроительной документацией о застройке и правилами землепользования и застройки (зонированием территорий), а также в случае предоставления земельного участка для нужд сельскохозяйственного производства или лесного хозяйства либо гражданину для индивидуального жилищного строительства, ведения личного подсобного хозяйства.
#
#О признании не противоречащим Конституции РФ пункта 12 статьи 30 см. Постановление Конституционного Суда РФ от 23.04.2004 N 8-П.
#
#12. Иностранным гражданам, лицам без гражданства и иностранным юридическим лицам земельные участки для строительства могут предоставляться в порядке, установленном настоящей статьей, в соответствии с пунктом 2 статьи 5, пунктом 3 статьи 15, пунктом 1 статьи 22 и пунктами 4 и 5 статьи 28 настоящего Кодекса.'''
    numb = '(\d[\d\.]*)'

    part = '((ч\.|част[а-я]*) ?' + numb + ')'
    parts = '(' + part + '.*?)'

    article = '((ст\.|стать[а-я]*) ?' + numb + ')'
    articles = '(' + article + '.*?)'

    paragraph = '((п\.|пункт[а-я]*) ?' + numb + ')'
    paragraphs = '(' + paragraph + '.*?)'

    KK = '( УК[ \.,]|КоАП|УПК|КОАП|[Уу]головн.*? [Кк]одекс.?|[Кк]одекс.*? об административных правонарушениях)'
    string = re.sub(KK, '\\1@#@', string)
    strings = string.split('@#@')

    pap = '(' + parts + '|' + articles + '|' + paragraphs + ')'

    norm_act_all = '(' + pap + '*' + KK + ')'
    out = []
    for line in strings:
        norm_act = re.findall(norm_act_all, line)
        if norm_act != []:
            norm_act = norm_act[0]
            if norm_act != '':
                out.append(norm_act[0])
    return out

def clean_act(acts):
    out = {}
    numb = '(\d[\d\.]*)'
    part = '((ч\.|част[а-я]*) ?' + numb + ')'
    article = '((ст\.|стать[а-я]*) ?' + numb + ')'
    paragraph = '((п\.|пункт[а-я]*) ?' + numb + ')'
    for act in acts:
        actn = re.sub(part, 'p_\\3_', act)
        actn = re.sub(article, 'a_\\3_', actn)
        actn = re.sub(paragraph, 'f_\\3_', actn)
        actn = re.sub('(УК|УПК|[Уу]головного [Кк]одекса)', 'k_KK_', actn)
        actn = re.sub('(КоАП|КОАП)', 'k_KOAP_', actn)
        actn = re.sub('[ ,]', 's_s_', actn)
        actn = re.findall('[a-z]_.*?_', actn)
        line = ''
        for i in actn:
            line += i
        line = re.sub('(s_s_(s_s_)+)', '_split_', line)
        line = line.replace('s_s_', '')
        line = line.replace('__', '_')
        out[act] = line
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
        if arr[act] != []:
            out[symbols] = str(arr[act][0].entity_id).replace("UUID('", '').replace("')", '')
        source = source[last_symbol:]
        len_of_line += last_symbol
    return out

def tomita_out(file_name, source_name, tomita_path):
    """function to run all together"""
    out = list_make(text_make(tomita_path + '/' + file_name), source_name, tomita_path)
    return out