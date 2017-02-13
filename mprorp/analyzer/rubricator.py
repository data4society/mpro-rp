"""functions for prepare documents, learning rubrication model and compute rubric """
import mprorp.analyzer.db as db
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import math
import tensorflow as tf
import random
import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from mprorp.analyzer.save_info import save_info
import pickle as pickle
from mprorp.utils import home_dir
from sqlalchemy.orm.attributes import flag_modified

# initialization mystem
mystem_analyzer = Mystem(disambiguation=False)
# words number for tf-idf model
feature_selection = 2 # 1 - entropy_difference, 2 - mutual_information
optimal_features_number = 50
tf_steps = 40000
lr=10
l2 = 0.005
# words to exclude from model

# one document morphological analysis regular

run_stop_lemmas = False # Использование файла для чтения стоп-лемм
stop_lemmas_filename = home_dir + '/lex_count' # Имя файла, содержащего стоп-леммы
stop_lemmas_count = 1000 # Порог, при превышении которго лемма считается не интересной и попадает в стоп-леммы

eliminate_once_found_lemma = True # Исключаются те леммы, которые встретились только в одном документе


def get_stop_lemmas(training_set=""):

    stop_lemmas = []
    if run_stop_lemmas:

        input_file = open(stop_lemmas_filename, 'rb')
        lex_count = pickle.load(input_file)
        input_file.close()

        for cur_lex_count in lex_count:
            if cur_lex_count[1] < stop_lemmas_count:
                break
            stop_lemmas.append(cur_lex_count[0])

    else:
        stop_lemmas = ['в', 'на', 'из', 'он', 'что', 'и', 'это', 'по', 'быть', 'этот', 'она', 'они', 'так', 'как', 'тогда',
               'те', 'также', 'же', 'то', 'за', 'который', 'после', 'оно', 'с', 'к', 'у', 'о', 'об', 'его', 'а',
               'не', 'год', 'во', 'весь', 'было', 'свой', 'тот', 'все', 'если', 'тогда', 'от', 'уже', 'д', 'м', 'при',
               'под', 'со', 'ее', 'сам', 'ранее', 'для', 'до', 'будет', 'или', 'их', 'я', 'но', 'нужный', 'ул',
               'время', 'наш', 'самый', 'вы', 'мы', 'любой', 'еще', 'нужно', 'до', 'любая', 'нами', 'такой', 'где',
               'один', 'рассказывать', 'находиться', 'становиться', 'иметь', 'быль', 'может', 'можно', 'очень', 'чтобы',
               'раз', 'каждый', 'новый', 'хороший', 'только', 'мочь', 'даже', 'себя', 'приходить', 'два', 'когда',
               'того', 'кто', 'многий', 'большой', 'маленький', 'первый', 'эта', 'другой',
               'девать', 'иметь', 'быль', 'рассказывать', 'мочь', 'смочь', 'время', 'ранее']

    # if eliminate_once_found_lemma:
    #
    #     lex_doc_count = {}
    #
    #     mystem_analyzer.start()
    #     for doc_id in db.get_set_docs(training_set):
    #         lex_doc = run_eliminate_once_found_lemma2(doc_id)
    #         for lex_doc_key in lex_doc.keys():
    #             if lex_doc_key in lex_doc_count:
    #                 lex_doc_count[lex_doc_key] += 1
    #             else:
    #                 lex_doc_count[lex_doc_key] = 1
    #     mystem_analyzer.close()
    #
    #     for key_lex_doc_count in lex_doc_count.keys():
    #         if lex_doc_count[key_lex_doc_count] == 1:
    #             stop_lemmas.append(key_lex_doc_count)

    return stop_lemmas


def run_eliminate_once_found_lemma2(doc_id):
    return db.doc_apply(doc_id, run_eliminate_once_found_lemma)


def run_eliminate_once_found_lemma(doc):
    return calculate_doc_lemmas(doc.stripped)


def is_word(mystem_element):
    """True if element is not space and have length """
    word = mystem_element.get('text', '')
    if len(word.strip()) > 0:
        return True
    return False


def is_sentence_end(mystem_element):
    """True if element is \\s or \n"""
    word = mystem_element.get('text', '')
    return word == '\\s' or word == '\n'


def morpho_doc2(doc_id):
    """wrap for morpho_doc with local session"""
    db.doc_apply(doc_id, morpho_doc)


def morpho_doc(doc, verbose=False):
    """morphologicapl analysis for document """
    doc_text = doc.stripped
    # mystem_analyzer.start()
    # new_morpho = mystem_analyzer.analyze(doc_text)
    new_morpho = mystem_analyzer.analyze(doc_text)

    morpho_list = []

    for element in new_morpho: # разрезаем

        if is_sentence_end(element):
            morpho_list.append(element)
        else:

            line = element.get('text', '')

            space_len = 0

            word_start = -1
            word_len = 0

            symbol_number = -1
            for symbol in line:

                symbol_number += 1

                if symbol == "'" or symbol == '"' or symbol == '»' or symbol == '«':

                    if space_len > 0: # добавим пробелы

                        cur_space = ' ' * space_len

                        new_element = {'text': cur_space}
                        if 'analysis' in element: new_element['analysis'] = element['analysis']
                        morpho_list.append(new_element)

                        space_len = 0

                    elif word_start > -1: # добавим слово

                        cur_word = line[word_start:(word_start + word_len)]

                        new_element = {'text': cur_word}
                        if 'analysis' in element: new_element['analysis'] = element['analysis']
                        morpho_list.append(new_element)

                        word_start = -1
                        word_len = 0

                    # добавим кавычку
                    new_element = {'text': symbol}
                    if 'analysis' in element: new_element['analysis'] = element['analysis']
                    morpho_list.append(new_element)

                elif symbol == " ":

                    if word_start > -1: # добавим слово

                        cur_word = line[word_start:(word_start + word_len)]

                        new_element = {'text': cur_word}
                        if 'analysis' in element: new_element['analysis'] = element['analysis']
                        morpho_list.append(new_element)

                        word_start = -1
                        word_len = 0

                    space_len += 1

                elif symbol == "\n":

                    if word_start > -1:  # добавим слово


                        cur_word = line[word_start:(word_start + word_len)]

                        new_element = {'text': cur_word}

                        if 'analysis' in element: new_element['analysis'] = element['analysis']

                        morpho_list.append(new_element)

                        word_start = -1

                        word_len = 0

                    new_element = {'text': '\n'}
                    morpho_list.append(new_element)
                elif symbol == "-":
                    if verbose:
                        print(line)
                    is_ok = False
                    if (line[word_start:(word_start + word_len)] == 'кое') or (line[word_start:(word_start + word_len)] == 'кой'):
                        is_ok = True
                    for word in ['то', 'либо', 'нибудь', 'таки']:
                        if symbol_number + len(word) < len(line) and line[symbol_number + 1: symbol_number + 1 + len(word)] == word:
                            is_ok = True
                            break
                    if not is_ok:
                        if word_start > -1:  # добавим слово

                            cur_word = line[word_start:(word_start + word_len)]
                            if verbose:
                                print('    ', cur_word)
                            new_element = {'text': cur_word}
                            if 'analysis' in element:
                                new_element['analysis'] = []
                                for num in range(len(element['analysis'])):
                                    new_element['analysis'].append(element['analysis'][num].copy())
                                    lex = element['analysis'][num]['lex']
                                    symb_num = lex.find('-')
                                    if symb_num > -1:
                                        new_element['analysis'][num]['lex'] = lex[:symb_num]

                                        element['analysis'][num]['lex'] = lex[symb_num + 1:] if len(lex) > symb_num + 1 else ''
                                        if verbose:
                                            print(lex, new_element['analysis'][num]['lex'], element['analysis'][num]['lex'], cur_word)
                            morpho_list.append(new_element)

                            word_start = -1
                            word_len = 0

                        # добавим дефис
                        new_element = {'text': symbol}
                        if 'analysis' in element:
                            # new_element['analysis'] = element['analysis']
                            if verbose:
                                print('analysis: ', element['analysis'])
                        morpho_list.append(new_element)
                    else:
                        word_len += 1
                else:

                    if space_len > 0: # добавим пробелы

                        cur_space = ' ' * space_len

                        new_element = {'text': cur_space}
                        if 'analysis' in element: new_element['analysis'] = element['analysis']
                        morpho_list.append(new_element)

                        space_len = 0

                    if word_start == -1:
                        word_start = symbol_number
                        word_len = 1
                    else:
                        word_len += 1

            if space_len > 0: # добавим пробелы

                cur_space = ' ' * space_len

                new_element = {'text': cur_space}
                if 'analysis' in element: new_element['analysis'] = element['analysis']

                morpho_list.append(new_element)

            elif word_start > -1: # добавим слово

                cur_word = line[word_start:(word_start + word_len)]

                new_element = {'text': cur_word}
                if 'analysis' in element: new_element['analysis'] = element['analysis']
                morpho_list.append(new_element)

    for i in range(len(morpho_list) - 1): # переставляем
        if i > 0:
            if morpho_list[i - 1]['text'] == ' ' and morpho_list[i]['text'] == '"' and morpho_list[i + 1]['text'] == '\\s':
                morpho_list[i], morpho_list[i + 1] = morpho_list[i + 1], morpho_list[i]

    sentence_index = 0
    word_index = 0
    start_offset = 0
    start_offset2 = 0

    for element in morpho_list: # нумеруем
        if is_sentence_end(element):
            if word_index != 0:
                sentence_index += 1
                word_index = 0
            if element.get('text', '') == '\n':
                start_offset2 += 1
        else:
            line = element.get('text', '')
            line_len = len(line)

            if not (line[0] == ' '):
                element['start_offset'] = start_offset
                element['end_offset'] = start_offset + line_len - 1
                element['start_offset2'] = start_offset2
                element['end_offset2'] = start_offset2 + line_len - 1
                element['word_index'] = word_index
                element['sentence_index'] = sentence_index

                word_index += 1
            start_offset += line_len
            start_offset2 += line_len

    if start_offset2 != len(doc_text):
        print('Error: different length: text - ', len(doc_text), ' last symbol in morpho: ', start_offset2)
        print('    doc_id: ', doc.doc_id)
    doc.morpho = morpho_list
    # mystem_analyzer.close()


# counting lemmas frequency for one document
def lemmas_freq_doc2(doc_id, stop_lemmas = None):
    """wrap for lemmas_freq_doc with local session"""
    db.doc_apply(doc_id, lemmas_freq_doc, stop_lemmas)


def lemmas_freq_doc(doc, stop_lemmas = None):
    """ extraction lemmas from morpho """
    if stop_lemmas is None:
        stop_lemmas = get_stop_lemmas()
    lemmas = {}
    morpho = doc.morpho
    for i in morpho:
        # if this is a word
        if 'analysis' in i.keys():
            # if there is few lex
            if len(i['analysis']):
                for l in i.get('analysis', []):
                    if l.get('lex', False):
                        if (not l['lex'] in stop_lemmas) & (l.get('wt', 0) > 0):
                            lemmas[l['lex']] = lemmas.get(l['lex'], 0) + l.get('wt', 1)
            else:
                # english word or number or smth like this
                word = i.get('text', '')
                # take word, don't take number
                if (len(word) > 0) and not word.isdigit():
                    lemmas[word] = lemmas.get(word, 0) + 1
    doc.lemmas = lemmas


# compute idf and object-features matrix for training set
# idf for calc features of new docs
# object-features for learning model
# doc_index links doc_id and row index in object-features
# lemma_index links lemmas and column index in object-features
def idf_object_features_set(set_id):
    """ compute idf and object-features matrix for training set """
    # idf for calc features of new docs
    # object-features for learning model
    # doc_index links doc_id and row index in object-features
    # lemma_index links lemmas and column index in object-features

    # get lemmas of all docs in set
    docs = db.get_lemmas_freq(set_id)

    # document frequency - number of documents with lemma
    doc_freq = {}
    # number (sum of weights) of lemmas in document
    doc_size = {}
    # index of lemma in overall list
    lemma_index = {}
    # lemma counter in overall list
    lemma_counter = 0
    # document index
    doc_index = {}
    # document counter in overall list
    doc_counter = 0

    for doc_id in docs:
        # initialize doc_size
        doc_size[doc_id] = 0
        # add document in overall list by giving index
        doc_index[doc_id] = doc_counter
        doc_counter += 1
        # count lemmas of doc
        for lemma in docs[doc_id]:
            # increase number of docs with lemma
            doc_freq[lemma] = doc_freq.get(lemma, 0) + 1
            # increase number of lemmas in document
            doc_size[doc_id] += docs[doc_id][lemma]

    # compute idf
    idf = {}
    for lemma in doc_freq:
        idf[lemma] = - math.log(doc_freq[lemma]/doc_counter)

    # and lemmas add in overall list by giving index
    for lemma in idf:
        if idf[lemma] != 0:
            lemma_index[lemma] = lemma_counter
            lemma_counter += 1

    # initialization objects-features matrix
    object_features = np.zeros((doc_counter, lemma_counter))

    # fill objects-features matrix
    for doc_id in docs:
        doc_lemmas = docs[doc_id]
        for lemma in doc_lemmas:
            if lemma_index.get(lemma, -1) != -1:
                object_features[doc_index[doc_id], lemma_index[lemma]] = \
                    doc_lemmas[lemma] / doc_size[doc_id] * idf[lemma]

    # check features with 0 for all documents
    feat_max = np.sum(object_features, axis=0)
    # print_lemmas(set_id, [k for k, v in enumerate(feat_max) if v == 0], lemma_index, idf)
    # check documents with 0 for all lemmas
    # print(np.min(np.sum(object_features, axis=1)))
    # print('for set_id: ', set_id)
    # print('save idf: ', idf)

    # save to db: idf, indexes and object_features
    db.put_training_set_params(set_id, idf,  doc_index, lemma_index, object_features)

    # print(idf)
    # print(doc_index)
    # print(lemma_index)
    # print(object_features)


def sigmoid_array(x):
    """sigmoid for every value of array x"""
    for l in range(len(x)):
        x[l] = 1/(1 + math.exp(-x[l]))
    return x


def sigmoid(x):
    """sigmoid for value x"""
    return 1/(1 + math.exp(-x))


# bigger value is worse
def entropy_difference(feature, answers, num_lemma):
    """compute entropy criteria for feature and answers"""
    f_max = np.max(feature)
    f_min = np.min(feature)
    # check is it unsound feature
    if f_max == f_min:
        # print('lemma 0: ', num_lemma)
        return 10000
    step = (f_max - f_min) / 1000
    p = [[0, 0] for _ in range(1000)]
    sum_p = len(feature)
    for j in range(len(feature)):
        index = math.trunc((feature[j] - f_min)/step)
        if index == 1000:
            index = 999
        p[index][answers[j]] += 1
    # difference between entropy feature+answers and just feature
    result = 0
    for i in range(1000):
        if (p[i][0] != 0) & (p[i][1] != 0):
            result += math.log2((p[i][0] + p[i][1]) / sum_p) * (p[i][0] + p[i][1]) / sum_p - \
                      math.log2(p[i][0] / sum_p) * (p[i][0]) / sum_p - \
                      math.log2(p[i][1] / sum_p) * (p[i][1]) / sum_p
    # entropy answers
    all_answers = len(answers)
    positive_answers = sum(answers) / all_answers
    negative_answers = 1 - positive_answers
    if (positive_answers == 0) or negative_answers == 0:
        entropy_answers = 0
    else:
        entropy_answers = - positive_answers * math.log2(positive_answers) - \
                          negative_answers * math.log2(negative_answers)

    # difference between (feature entropy + answers entropy) and (feature + answers) entropy
    if entropy_answers - result < 0:
        print('negative information', num_lemma, entropy_answers - result)
    return - (entropy_answers - result)


def mutual_information(feature, answers, num_lemma):
    # http://nlp.stanford.edu/IR-book/html/htmledition/mutual-information-1.html
    N = np.zeros((2, 2), dtype=int)
    for j in range(len(feature)):
        if feature[j] == 0:
            if answers[j] == 0:
                N[0, 0] += 1
            else:
                N[0, 1] += 1
        else:
            if answers[j] == 0:
                N[1, 0] += 1
            else:
                N[1, 1] += 1
    sumN = N[0, 0] + N[1, 0] + N[0, 1]+N[1, 1]
    if num_lemma < 20:
        print(N[0,:], N[1,:])
    def part(i, j):
        if N[i, j] > 0:
            return N[i, j]/sumN * math.log2(sumN * N[i,j]/(N[i, 0]+N[i, 1])/(N[0, j]+N[1, j]))
        else:
            return 0

    return - (part(1,1) + part(0,1) + part(1,0) + part(0,0))


# print lemmas with index in numbers, its index and idf
def print_lemmas(set_id, numbers, lemmas=None, idf=None):
    if idf is None:
        idf = {}
    if lemmas is None:
        lemmas = db.get_lemma_index(set_id)
    my_lemmas = [k for k in lemmas if lemmas[k] in numbers]
    # print(numbers)
    print(my_lemmas)
    # print([idf.get(k, '') for k in my_lemmas])
    # for i in numbers:
    #     m
    #     print(i, [k for k in lemmas if lemmas[k] == i])


# learn model for rubrication
def learning_rubric_model(set_id, rubric_id, savefiles = False, verbose=False):
    """learn model for rubrication"""
    # get answers for rubric
    answers = db.get_rubric_answers(set_id, rubric_id)
    # get object_features, lemma_index, doc_index
    if verbose:
        print('answers: ', len(answers), sum(list(answers.values())))
    doc_index, object_features = db.get_doc_index_object_features(set_id)

    # print(np.min(np.sum(object_features, axis=0)))
    # print(np.min(np.sum(object_features, axis=1)))

    doc_number = len(doc_index)
    # answers_index - answers by indexes, answers_array - array for compute cross_entropy in tensorflow
    answers_array = np.zeros((doc_number, 1))
    answers_index = np.zeros(doc_number, dtype=int)
    for doc_id in doc_index:
        answers_index[doc_index[doc_id]] = answers[doc_id]
        # answers_array[doc_index[doc_id], 0] = answers[doc_id] * 2 - 1
        answers_array[doc_index[doc_id], 0] = answers[doc_id]

    # if we know answers, we can select most important features (mif):
    # mif[k] = l:
    # feature k from object_features is used in position l, if l >= 0
    # if feature k ins not most important, l = -1
    features_number = len(object_features[0])
    # mif = np.empty(features_number)
    # mif.fill(-1)
    mif_number = features_number
    mif_indexes = []
    use_mif = features_number > optimal_features_number
    if use_mif:
        mif_number = optimal_features_number
        feature_entropy = np.zeros(features_number)
        for i in range(features_number):
            # compute Entropic Criterion for feature i
            if feature_selection == 1:
                feature_entropy[i] = entropy_difference(object_features[:, i], answers_index, i)
            else:
                feature_entropy[i] = mutual_information(object_features[:, i], answers_index, i)
                if i < 20:
                    print('MI', feature_entropy[i])
            if i < 20:
                print('E', entropy_difference(object_features[:, i], answers_index, i))

                print('---')

        good_numbers = np.argsort(feature_entropy)
        for i in range(optimal_features_number):
            # mif[good_numbers[i]] = i
            mif_indexes.append(int(good_numbers[i]))
        # print_lemmas(set_id, good_numbers[0:100])
        # print(feature_entropy[good_numbers[0:100]])
    else:
        for i in range(features_number):
            mif_indexes.append(i)

    x = tf.placeholder(tf.float32, shape=[None, mif_number])
    y_ = tf.placeholder(tf.float32, shape=[None, 1])
    w = tf.Variable(tf.truncated_normal([mif_number, 1], stddev=0.1))
    b = tf.Variable(0.00001)

    y = tf.matmul(x, w) + b
    # take probability (sigmoid) when answer is true and -sigmoid (instead 1-sigmoid) otherwise
    # cross_entropy_array = tf.sigmoid(y) * y_
    # cross_entropy = tf.reduce_mean(
    #     tf.nn.softmax_cross_entropy_with_logits(y, y_))
    cross_entropy_array = tf.log(tf.sigmoid(y)) * y_ + tf.log(1- tf.sigmoid(y)) * (1 - y_)

    cross_entropy = - tf.reduce_mean(cross_entropy_array) + tf.reduce_mean(w * w) * l2

    train_step = tf.train.GradientDescentOptimizer(learning_rate=lr).minimize(cross_entropy)
    init = tf.initialize_all_variables()

    sess = tf.Session()
    sess.run(init)

    indexes = [i for i in range(doc_number)]
    # big_counter = 0
    if verbose:
        print('object_features:')
        if use_mif:
            print(object_features[10, :][mif_indexes])
        else:
            print(object_features[10, :])
    for i in range(tf_steps):
        # if i == big_counter * 100:
        #     big_counter = round(i/100) + 1
        #     print(i)
        if doc_number > 150:
            local_answers = answers_array[indexes[0:100], :]
            if use_mif:
                sess.run(train_step,
                         feed_dict={x: object_features[indexes[0:100], :][:, mif_indexes], y_: local_answers})
            else:
                sess.run(train_step, feed_dict={x: object_features[indexes[0:100], :], y_: local_answers})
            random.shuffle(indexes)
        else:
            if use_mif:
                sess.run(train_step, feed_dict={x: object_features[:, mif_indexes], y_: answers_array})
            else:
                sess.run(train_step, feed_dict={x: object_features, y_: answers_array})
        # my_cea = cross_entropy_array.eval(sess)
        # print(my_cea)
        # my_w = w.eval(sess)
        # my_b = b.eval(sess)
        # print(i, (sigmoid(np.dot(np.asarray(object_features), my_W) + my_b) * np.asarray(answers_array)))

    model = w.eval(sess)[:, 0]
    model = model.tolist()
    model.append(float(b.eval(sess)))
    if savefiles is True:
        session = Driver.db_session()
        my_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
        lemm_dic = my_set.lemma_index
        x = open('info_' + str(set_id) + '.py', 'w', encoding='utf-8')
        x.write("rubric_id = '" + str(rubric_id) + "'\n")
        x.write("set_id = '" + str(set_id) + "'\n")
        x.write('lemm_dic = ' + str(my_set.lemma_index) + '\n')
        x.write('model = ' + str(model) + '\n')
        x.write('mif_indexes = ' + str(mif_indexes) + '\n')
        x.write('mif_number = ' + str(mif_number))
        x.close()
        save_info(lemm_dic, mif_indexes, model, set_id)
    db.put_model(rubric_id, set_id, model, mif_indexes, mif_number)

    # print(W.eval(sess))
    # print(b.eval(sess))


# print lemmas with index in numbers, its index and idf
# def print_lemmas(set_id, numbers, lemmas=None, idf=None):
#     if idf is None:
#         idf = {}
#     if lemmas is None:
#         lemmas = db.get_lemma_index(set_id)
#     my_lemmas = [k for k in lemmas if lemmas[k] in numbers]
    # print(numbers)
    # print(my_lemmas)
    # print([idf.get(k, '') for k in my_lemmas])
    # for i in numbers:
    #     m
    #     print(i, [k for k in lemmas if lemmas[k] == i])


# learn model for rubrication
def learning_rubric_model_coeffs(set_id, doc_coefficients, rubric_id, savefiles = False, verbose=False):
    """learn model for rubrication with different negative sets"""
    # doc_coefficients = {'set_id_1': coeff_1, 'set_id_2': coeff_2, ...}
    sets_coef = {}
    for set_co_id in doc_coefficients:
        sets_coef[set_co_id] = db.get_set_docs(set_co_id)
    # get answers for rubric
    answers = db.get_rubric_answers(set_id, rubric_id)
    if verbose:
        print('answers: ', len(answers), sum(list(answers.values())))
        # print(answers)
    # get object_features, lemma_index, doc_index
    doc_index, object_features = db.get_doc_index_object_features(set_id)

    doc_number = len(doc_index)

    # answers_index - answers by indexes, answers_array - array for compute cross_entropy in tensorflow
    coeffs_array = np.zeros((doc_number, 1))
    answers_array = np.zeros((doc_number, 1))
    answers_index = np.zeros(doc_number, dtype=int)
    for doc_id in doc_index:
        answers_index[doc_index[doc_id]] = answers[doc_id]
        answers_array[doc_index[doc_id], 0] = answers[doc_id] * 2 - 1
        for set_co_id in doc_coefficients:
            if doc_id in sets_coef[set_co_id]:
                coeffs_array[doc_index[doc_id], 0] = doc_coefficients[set_co_id]
                break

    # if we know answers, we can select most important features (mif):
    # mif[k] = l:
    # feature k from object_features is used in position l, if l >= 0
    # if feature k ins not most important, l = -1
    features_number = len(object_features[0])
    # mif = np.empty(features_number)
    # mif.fill(-1)
    mif_number = features_number
    mif_indexes = []
    use_mif = features_number > optimal_features_number
    if use_mif:
        mif_number = optimal_features_number
        feature_entropy = np.zeros(features_number)
        for i in range(features_number):
            # compute Entropic Criterion for feature i
            feature_entropy[i] = entropy_difference(object_features[:, i], answers_index, i)
        good_numbers = np.argsort(feature_entropy)
        for i in range(optimal_features_number):
            # mif[good_numbers[i]] = i
            mif_indexes.append(int(good_numbers[i]))
        # print_lemmas(set_id, good_numbers[0:100])
        # print(feature_entropy[good_numbers[0:100]])
    else:
        for i in range(features_number):
            mif_indexes.append(i)

    x = tf.placeholder(tf.float32, shape=[None, mif_number])
    y_ = tf.placeholder(tf.float32, shape=[None, 1])
    co = tf.placeholder(tf.float32, shape=[None, 1])
    w = tf.Variable(tf.truncated_normal([mif_number, 1], stddev=0.1))
    b = tf.Variable(0.00001)

    y = tf.matmul(x, w) + b
    # take probability (sigmoid) when answer is true and -sigmoid (instead 1-sigmoid) otherwise
    cross_entropy_array = tf.sigmoid(y) * y_ * co
    cross_entropy = - tf.reduce_mean(cross_entropy_array)

    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
    init = tf.initialize_all_variables()

    sess = tf.Session()
    sess.run(init)

    indexes = [i for i in range(doc_number)]
    # big_counter = 0
    for i in range(5000):
        # if i == big_counter * 100:
        #     big_counter = round(i/100) + 1
        #     print(i)
        if doc_number > 150:
            local_answers = answers_array[indexes[0:100], :]
            local_coeffs = coeffs_array[indexes[0:100], :]
            if use_mif:
                sess.run(train_step,
                         feed_dict={x: object_features[indexes[0:100], :][:, mif_indexes],
                                    y_: local_answers, co: local_coeffs})
            else:
                sess.run(train_step, feed_dict={x: object_features[indexes[0:100], :],
                                                y_: local_answers, co: local_coeffs})
            random.shuffle(indexes)
        else:
            if use_mif:
                sess.run(train_step, feed_dict={x: object_features[:, mif_indexes],
                                                y_: answers_array, co: local_coeffs})
            else:
                sess.run(train_step, feed_dict={x: object_features, y_: answers_array, co: local_coeffs})

        # if verbose:
        #     if i % 500 == 0:
        #         my_cea = cross_entropy_array.eval(sess)
        #         print(my_cea)
        #         my_w = w.eval(sess)
        #         my_b = b.eval(sess)
        #         print(i, (sigmoid(np.dot(np.asarray(object_features), my_W) + my_b) * np.asarray(answers_array)))

    model = w.eval(sess)[:, 0]
    model = model.tolist()
    model.append(float(b.eval(sess)))
    if savefiles is True:
        session = Driver.db_session()
        my_set = session.query(TrainingSet).filter(TrainingSet.set_id == set_id).one()
        lemm_dic = my_set.lemma_index
        x = open('info_' + str(set_id) + '.py', 'w', encoding='utf-8')
        x.write("rubric_id = '" + str(rubric_id) + "'\n")
        x.write("set_id = '" + str(set_id) + "'\n")
        x.write('lemm_dic = ' + str(my_set.lemma_index) + '\n')
        x.write('model = ' + str(model) + '\n')
        x.write('mif_indexes = ' + str(mif_indexes) + '\n')
        x.write('mif_number = ' + str(mif_number))
        x.close()
        save_info(lemm_dic, mif_indexes, model, set_id)
    db.put_model(rubric_id, set_id, model, mif_indexes, mif_number)

    # print(W.eval(sess))
    # print(b.eval(sess))


# take 1 doc and few rubrics
# save in DB doc_id, rubric_id and YES or NO
# rubrics is a dict. key = rubric_id, value = None or set_id
# value = set_id: use model, learned with this trainingSet
def spot_doc_rubrics2(doc_id, rubrics, verbose=False):
    """wrap for spot_doc_rubrics with local session"""
    db.doc_apply(doc_id, spot_doc_rubrics, rubrics, verbose=verbose)


def spot_doc_rubrics(doc, rubrics, session=None, commit_session=True, verbose=False):
    """spot rubrics for document"""
    # get lemmas by doc_id
    lemmas = doc.lemmas
    # compute document size
    doc_size = 0
    for lemma in lemmas:
        doc_size += lemmas[lemma]
    # models for rubrics
    models = {}
    negative_rubrics = {}
    train_set = {}
    probabilities = {}
    # fill set_id in rubrics and data in models
    for rubric_dict in rubrics:
        rubric_id = rubric_dict['rubric_id']
        negative_rubrics[rubric_id] = rubric_dict['rubric_minus_id']
        train_set_id = db.get_set_id_by_name(rubric_dict['set_name'])
        if train_set_id is None or train_set_id == '':
            continue
        train_set[rubric_id] = train_set_id
        # correct_answers[rubric_id] = db.get_rubric_answer_doc(doc_id, rubric_id)
        models[rubric_id] = db.get_model(rubric_id, train_set_id, session)
        # get_model: return {'model': model[0], 'features': model[1],
        #                   'features_num': model[2], 'model_id': str(model[3])}
        if verbose:
            print('Для рубрики ', rubric_id, ' используется модель ', models[rubric_id])
    # get dict with idf and lemma_index for each set_id
    # sets[...] is dict: {'idf':..., 'lemma_index': ...}
    sets = db.get_idf_lemma_index_by_set_id(train_set.values(), session)
    for set_id in sets:
        # if verbose:
        #     print('sets: ', set_id, sets[set_id])
        # compute idf for doc_id (lemmas) and set_id
        idf_doc = {}
        for lemma in lemmas:
            idf_doc[lemma] = lemmas[lemma] * sets[set_id]['idf'].get(lemma, 0) / doc_size
        sets[set_id]['idf_doc'] = idf_doc
    # for each rubric
    answers = []
    result = []
    for rubric_id in train_set:
        set_id = train_set[rubric_id]
        mif_number = models[rubric_id]['features_num']
        lemma_index = sets[set_id]['lemma_index']
        features_array = np.zeros(len(lemma_index), dtype=float)
        # form features row with size and order like in object_features of training set
        for lemma in lemmas:
            # lemma index in lemmas of set
            ind_lemma = lemma_index.get(lemma, -1)
            # if lemma from doc is in lemmas for training set
            if ind_lemma > -1:
                features_array[ind_lemma] = sets[set_id]['idf_doc'][lemma]
        # take most important features of model
        mif = features_array[models[rubric_id]['features']]
        # add 1 for coefficient b in model
        # mif[mif_number] = 1
        mif.resize(mif_number + 1)
        mif[mif_number] = 1
        probability = sigmoid(np.dot(mif, models[rubric_id]['model']))
        probabilities[rubric_id] = probability
        if verbose:
            print('Вероятность: ', probability)
        if probability > 0.5:
            answers.append(rubric_id)
        else:
            answers.append(negative_rubrics[rubric_id])
        result.append(
                {'rubric_id': rubric_id, 'result': round(probability), 'model_id': models[rubric_id]['model_id'],
                 'doc_id': doc.doc_id, 'probability': probability})
        result.append(
                {'rubric_id': negative_rubrics[rubric_id], 'result': 1 - round(probability),
                 'model_id': models[rubric_id]['model_id'],
                 'doc_id': doc.doc_id, 'probability': probability})

    db.put_rubrics(result, session, commit_session)
    if verbose:
        print(answers)
    doc.rubric_ids = answers
    if doc.meta is None:
        doc.meta = dict()
    doc.meta['rubric_probabilities'] = probabilities
    flag_modified(doc, "meta")


# take 1 rubric and all doc from test_set
# save in DB doc_id, rubric_id and YES or NO
def spot_test_set_rubric(test_set_id, rubric_id, training_set_id=None):
    """spot rubrics for all documents from test_set"""
    # get lemmas
    docs = db.get_lemmas_freq(test_set_id)
    docs_size = {}

    # compute document size
    for doc_id in docs:
        lemmas = docs[doc_id]
        docs_size[doc_id] = 0
        for lemma in lemmas:
            docs_size[doc_id] += lemmas[lemma]

    # models for rubrics
    if training_set_id is None:
        training_set_id = db.get_set_id_by_rubric_id(rubric_id)
    model = db.get_model(rubric_id, training_set_id)
    # print('model')
    # print(model)
    mif_number = model['features_num']
    idf_lemma_index = db.get_idf_lemma_index_by_set_id([training_set_id])[training_set_id]
    lemma_index = idf_lemma_index['lemma_index']
    training_idf = idf_lemma_index['idf']

    answers = []
    for doc_id in docs:
        if docs_size[doc_id]:
            # print(doc_id)
            features_array = np.zeros(len(lemma_index), dtype=float)
            lemmas = docs[doc_id]
            for lemma in lemmas:
                # lemma index in lemmas of training set
                ind_lemma = lemma_index.get(lemma, -1)
                # if lemma from doc is in lemmas for training set
                if ind_lemma > -1:
                    features_array[ind_lemma] = lemmas[lemma] * training_idf[lemma] / docs_size[doc_id]
            mif = features_array[model['features']]
            mif.resize(mif_number + 1)
            mif[mif_number] = 1
            # print(mif)
            probability = sigmoid(np.dot(mif, model['model']))
            # print(probability)
            answers.append({'result': round(probability), 'model_id': model['model_id'],
                            'rubric_id': rubric_id, 'doc_id': doc_id, 'probability': probability})
        else:
            answers.append({'result': 0, 'model_id': model['model_id'],
                            'rubric_id': rubric_id, 'doc_id': doc_id, 'probability': 0})

    db.put_rubrics(answers)
    return model['model_id']


# compute TP, FP, TN, FN, Precision, Recall and F-score on data from db
def f1_score(model_id, test_set_id, rubric_id, protocol_file_name=""):
    """compute TP, FP, TN, FN, Precision, Recall and F-score on data from db"""
    result = {'true_positive': 0, 'false_positive': 0, 'true_negative': 0, 'false_negative': 0}
    if protocol_file_name:
        result_docs = {'true_positive': [], 'false_positive': [], 'true_negative': [], 'false_negative': []}
    # right answers
    answers = db.get_rubric_answers(test_set_id, rubric_id)
    # rubrication results
    rubrication_result = db.get_rubrication_result(model_id, test_set_id, rubric_id)

    for key in rubrication_result:
        result_key = ''
        if rubrication_result[key] == answers[key]:
            if rubrication_result[key] == 1:
                result_key = 'true_positive'
            else:
                result_key = 'true_negative'
        else:
            if rubrication_result[key] == 1:
                result_key = 'false_positive'
            else:
                result_key = 'false_negative'
        result[result_key] += 1
        if protocol_file_name:
            result_docs[result_key].append(key)
    if (result['true_positive'] + result['false_positive']) > 0:
        result['precision'] = result['true_positive'] / (result['true_positive'] + result['false_positive'])
    else:
        result['precision'] = 0
    if (result['true_positive'] + result['false_negative']) > 0:
        result['recall'] = result['true_positive'] / (result['true_positive'] + result['false_negative'])
    else:
        result['recall'] = 0
    if (result['precision'] + result['recall']) > 0:
        result['f1'] = 2 * result['precision'] * result['recall'] / (result['precision'] + result['recall'])
    else:
        result['f1'] = 0
    if protocol_file_name:
        x = open(protocol_file_name, 'a', encoding='utf-8')
        x.write('ТЕКСТЫ ДОКУМЕНТОВ РАСРПДЕЛЕННЫЕ ПО ВАРИАНТАМ ОТВЕТА РУБРИКАТОРА:' + '\n')
        for result_key in result_docs:
            x.write('==========================================================' + '\n')
            x.write('==========================================================' + '\n')
            x.write(result_key + '\n')
            print_doc_texts_to_file(result_docs[result_key],x)
        x.close()
    return result


def print_doc_texts_to_file(doc_list, file):
    for doc_id in doc_list:
        file.write(db.get_doc_text(doc_id) + '\n')
        file.write('-----------------------------------------------------' + '\n')


def probabilities_score(model_id, test_set_id, rubric_id):
    """compute average probability for true and false answers"""
    result = {'true_average_probability': 0, 'false_average_probability': 0}
    # right answers
    answers = db.get_rubric_answers(test_set_id, rubric_id)
    # rubrication results
    rubrication_result = db.get_rubrication_probability(model_id, test_set_id, rubric_id)

    true_number = 0
    true_probability = 0
    false_number = 0
    false_probability = 0

    for key in rubrication_result:
        if answers[key]:
            true_number += 1
            true_probability += rubrication_result[key]
        else:
            false_number +=1
            false_probability += rubrication_result[key]

    if true_number:
        result['true_average_probability'] = true_probability / true_number

    if false_number:
        result['false_average_probability'] = false_probability / false_number

    return result


def calculate_indicators_lemmas(session=None):

    if session is None:
        session = Driver.db_session()

    lex_count = {}
    lex_count_150 = {}
    lex_doc_count = {}
    lex_doc_count_150 = {}

    docs = session.query(Document.stripped).filter(Document.stripped != '').all()
    # mystem_analyzer.start()
    for doc in docs:
        doc_text = doc[0]
        lex_doc = calculate_doc_lemmas(doc_text)
        for lex_doc_key in lex_doc.keys():

            if lex_doc_key in lex_count:
                lex_count[lex_doc_key] += lex_doc[lex_doc_key]
            else:
                lex_count[lex_doc_key] = lex_doc[lex_doc_key]

            if lex_doc_key in lex_doc_count:
                lex_doc_count[lex_doc_key] += 1
            else:
                lex_doc_count[lex_doc_key] = 1

            if len(doc_text) >= 150:
                if lex_doc_key in lex_count_150:
                    lex_count_150[lex_doc_key] += lex_doc[lex_doc_key]
                else:
                    lex_count_150[lex_doc_key] = lex_doc[lex_doc_key]

                if lex_doc_key in lex_doc_count_150:
                    lex_doc_count_150[lex_doc_key] += 1
                else:
                    lex_doc_count_150[lex_doc_key] = 1

    # mystem_analyzer.close()

    l = lambda x: x[1]
    #print(sorted(lex_count.items(), key=l, reverse=True))
    #print(sorted(lex_count_150.items(), key=l, reverse=True))
    #print(sorted(lex_doc_count.items(), key=l, reverse=True))
    #print(sorted(lex_doc_count_150.items(), key=l, reverse=True))
    output_file = open(home_dir + '/lex_count', 'wb')
    pickle.dump(sorted(lex_count.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()
    output_file = open(home_dir + '/lex_count_150', 'wb')
    pickle.dump(sorted(lex_count_150.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()
    output_file = open(home_dir + '/lex_doc_count', 'wb')
    pickle.dump(sorted(lex_doc_count.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()
    output_file = open(home_dir + '/lex_doc_count_150', 'wb')
    pickle.dump(sorted(lex_doc_count_150.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()


def calculate_indicators_lemmas_for_docs_with_ready_lemmas(session=None):

    if session is None:
        session = Driver.db_session()

    lex_count = {}
    lex_count_150 = {}
    lex_doc_count = {}
    lex_doc_count_150 = {}

    docs = session.query(Document.morpho, Document.stripped).all()
    for doc in docs:
        doc_morpho = doc[0]
        doc_text = doc[1]
        lex_doc = calculate_doc_lemmas(doc_morpho)
        for lex_doc_key in lex_doc.keys():

            if lex_doc_key in lex_count:
                lex_count[lex_doc_key] += lex_doc[lex_doc_key]
            else:
                lex_count[lex_doc_key] = lex_doc[lex_doc_key]

            if lex_doc_key in lex_doc_count:
                lex_doc_count[lex_doc_key] += 1
            else:
                lex_doc_count[lex_doc_key] = 1

            if len(doc_text) >= 150:
                if lex_doc_key in lex_count_150:
                    lex_count_150[lex_doc_key] += lex_doc[lex_doc_key]
                else:
                    lex_count_150[lex_doc_key] = lex_doc[lex_doc_key]

                if lex_doc_key in lex_doc_count_150:
                    lex_doc_count_150[lex_doc_key] += 1
                else:
                    lex_doc_count_150[lex_doc_key] = 1

    l = lambda x: x[1]
    #print(sorted(lex_count.items(), key=l, reverse=True))
    #print(sorted(lex_count_150.items(), key=l, reverse=True))
    #print(sorted(lex_doc_count.items(), key=l, reverse=True))
    #print(sorted(lex_doc_count_150.items(), key=l, reverse=True))
    output_file = open(home_dir + '/lex_count', 'wb')
    pickle.dump(sorted(lex_count.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()
    output_file = open(home_dir + '/lex_count_150', 'wb')
    pickle.dump(sorted(lex_count_150.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()
    output_file = open(home_dir + '/lex_doc_count', 'wb')
    pickle.dump(sorted(lex_doc_count.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()
    output_file = open(home_dir + '/lex_doc_count_150', 'wb')
    pickle.dump(sorted(lex_doc_count_150.items(), key=l, reverse=True), output_file, protocol=3)
    output_file.close()


def calculate_doc_lemmas(text):
    res_list = mystem_analyzer.analyze(text)
    lex_doc = {}
    for res in res_list:
        analysis = res.get('analysis', [])
        for analys in analysis:
            lex = analys.get('lex', '')
            if lex != '':
                if lex in lex_doc:
                    lex_doc[lex] += 1
                else:
                    lex_doc[lex] = 1
    return lex_doc


def calculate_doc_lemmas_morpho(morpho):
    lex_doc = {}
    for res in morpho:
        analysis = res.get('analysis', [])
        for analys in analysis:
            lex = analys.get('lex', '')
            if lex != '':
                if lex in lex_doc:
                    lex_doc[lex] += 1
                else:
                    lex_doc[lex] = 1
    return lex_doc