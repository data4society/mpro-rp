def save_info(lemm_dic, mif_indexes, model, set_id):
    lemms_in_use = []
    for lemma in lemm_dic:
        if lemm_dic[lemma] in mif_indexes:
            lemms_in_use.append(lemma)

    #print(len(lemms_in_use))
    #print(len(model))

    out_dic = {}
    for n in range(len(model) - 1):
        out_dic[model[n]] = lemms_in_use[n]
    a = [key for key in out_dic.keys()]
    a.sort()
    a.reverse()

    x = open('result_' + str(set_id) + '.txt', 'w', encoding='utf-8')
    for index in a:
        x.write(str(index) + ' : ' + str(out_dic[index]) + '\n')
    x.close()