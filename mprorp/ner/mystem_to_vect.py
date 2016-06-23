from mprorp.analyzer.pymystem3_w import Mystem
mystem = Mystem(disambiguation=False)
import re

def part_of_speech(gr):
    gr = re.findall('^\w*', gr)
    return gr[0]


def analisis_to_tamplate(analisis):
    tamplate_0 = [[0,0,0],[0,0,0,0,0,0,0,0,0],[0,0],[0,0,0,0,0],[0,0,0],[0,0],[0,0,0],[0,0,0],[0,0],[0,0],[0,0],[0,0]]
    tamplate = (('наст','непрош','прош'),('им','род','дат','вин','твор','пр','парт','местн','зват'),('ед','мн'),('деепр','инф','прич','изъяв','пов'),('кр','полн','притяж'),('прев','срав'),('1-л','2-л','3-л'),('муж','жен','сред'),('несов','сов'),('действ','страд'),('од','неод'),('пе','нп'))
    analisis = re.sub('=', ',', analisis)
    analisis = analisis.split(',')
    for m in range(len(tamplate)):
        attribute = tamplate[m]
        for n in range(len(attribute)):
            value = attribute[n]
            if value in analisis:
                tamplate_0[m][n] = 1
    return tamplate_0

def mystem_analysis_vect(gr):
    main_arr = []
    pos = part_of_speech(gr)
    if '(' in gr:
        analyzes = re.findall('\\((.*)\\)', gr)[0]
        analyzes = analyzes.split('|')
        for analisis in analyzes:
            tampl = analisis_to_tamplate(analisis)
            main_arr.append(tampl)
        return main_arr
    else:
        analisis = re.sub(pos + ',', '', gr)
        tampl = analisis_to_tamplate(analisis)
        main_arr.append(tampl)
        return main_arr

#примеры

a = mystem.analyze('В лесу стали.')
print(a)
# res = [[0,0,0],[0,0,0,0,0,0,0,0,0],[0,0],[0,0,0,0,0],[0,0,0],[0,0],[0,0,0],[0,0,0],[0,0],[0,0],[0,0],[0,0]]
# for analyse in a[0]['analysis']:
#     vects = mystem_analysis_vect(analyse['gr'])
#     len_vects = len(vects)
#     for vec in vects:
#         delta = (analyse['wt'] / len_vects)
#         print(vec)
#         delta2 = delta * [0,1,2]
#         res += delta
# print(res)

print(a[2]['analysis'][0]['gr'])
for i in mystem_analysis_vect(a[2]['analysis'][0]['gr']):
    print(i)

for word in a:
    if 'analysis' in word.keys():
        for i in word['analysis']:
            print(i['lex'],part_of_speech(i['gr']))

b = mystem.analyze('Я')
print(b[0]['analysis'][0]['gr'])
for i in mystem_analysis_vect(b[0]['analysis'][0]['gr']):
    print(i)

