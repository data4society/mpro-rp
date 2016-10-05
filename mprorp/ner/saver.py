def saver(word_to_num, words_for_embedding):
    out = []
    for word in words_for_embedding:
        if word not in word_to_num:
            out.append(word)
    return out