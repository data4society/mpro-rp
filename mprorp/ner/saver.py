def saver(word_to_num, words_for_embedding, training_set, tagname):
    out = []
    for word in words_for_embedding:
        if word not in word_to_num:
            out.append(word)
    x = open('words_not_used_' + str(training_set) + '_' + tagname + '.txt', 'a', encoding='utf-8')
    for word in out:
        x.write(word + '\n')
    x.close()