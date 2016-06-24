import re
import numpy as np


tamplate = (('наст', 'непрош', 'прош'), ('им', 'род', 'дат', 'вин', 'твор', 'пр', 'парт', 'местн', 'зват'),
            ('ед', 'мн'), ('деепр', 'инф', 'прич', 'изъяв', 'пов'), ('кр', 'полн', 'притяж'), ('прев', 'срав'),
            ('1-л', '2-л', '3-л'), ('муж', 'жен', 'сред'), ('несов', 'сов'),
            ('действ', 'страд'), ('од', 'неод'), ('пе', 'нп'))
vec_len = 0
for attr in tamplate:
    vec_len += len(attr)


def part_of_speech(gr):
    gr = re.findall('^\w*', gr)
    return gr[0]


def analisis_to_tamplate(analisis):
    # tamplate_0 = [[0,0,0],[0,0,0,0,0,0,0,0,0],[0,0],[0,0,0,0,0],[0,0,0],[0,0],[0,0,0],[0,0,0],[0,0],[0,0],[0,0],[0,0]]
    result = np.zeros(vec_len)

    analisis = re.sub('=', ',', analisis)
    analisis = analisis.split(',')
    pre_number = 0
    for attr in tamplate:
        for n in range(len(attr)):
            value = attr[n]
            if value in analisis:
                result[pre_number + n] = 1
        pre_number += len(attr)
    return result


def analyze(gr):
    main_arr = []
    pos = part_of_speech(gr)
    if '(' in gr:
        an = re.findall('(.*)=', gr)[0]
        an = re.sub(pos + ',', '', an)
        analyzes = re.findall('\\((.*)\\)', gr)[0]
        analyzes = analyzes.split('|')
        for analisis in analyzes:
            analisis = analisis + ',' + an
            tampl = analisis_to_tamplate(analisis)
            main_arr.append(tampl)
        # out = np.array(main_arr)
        return main_arr
    else:
        analisis = re.sub(pos + ',', '', gr)
        tampl = analisis_to_tamplate(analisis)
        main_arr.append(tampl)
        # out = np.array(main_arr)
        return main_arr

#примеры



# print(a[2]['analysis'][0]['gr'])
# for i in mystem_analysis_vect(a[2]['analysis'][0]['gr']):
#     print(i)
#
# for word in a:
#     if 'analysis' in word.keys():
#         for i in word['analysis']:
#             print(i['lex'],part_of_speech(i['gr']))
#
# b = mystem.analyze('Я')
# print(b[0]['analysis'][0]['gr'])
# for i in mystem_analysis_vect(b[0]['analysis'][0]['gr']):
#     print(i)
#
# c = mystem.analyze('Лес')
# print(c[0]['analysis'][0]['gr'])
# for i in mystem_analysis_vect(c[0]['analysis'][0]['gr']):
#     print(i)