import mprorp.analyzer.db as db
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import math
import tensorflow as tf
import random


mystem_analyzer = Mystem(disambiguation=False)
status = {'morpho': 2, 'lemmas': 3, 'rubrics': 4}
rubrics_for_regular = {u'd2cf7a5f-f2a7-4e2b-9d3f-fc20ea6504da': None}
optimal_features_number = 300
stop_lemmas = ['в', 'на', 'из', 'он', 'что', 'и', 'это', 'по', 'быть', 'этот', 'она', 'они', 'так', 'как', 'тогда',
               'те', 'также', 'же', 'то', 'за', 'который', 'после', 'оно', 'с', 'к', 'у', 'о', 'об', 'его', 'а',
               'не', 'год', 'во', 'весь', 'было', 'свой', 'тот', 'все']
                # 'под', 'со', '', '', '', '', '', '', '', '', ''


# one document morphological analysis regular
def regular_morpho(doc_id):
    morpho_doc(doc_id, status['morpho'])


# one document morphological analysis
def morpho_doc(doc_id, change_status=0):
    text = db.get_doc(doc_id)
    mystem_analyzer.start()
    new_morpho = mystem_analyzer.analyze(text)
    db.put_morpho(doc_id, new_morpho, change_status)
    mystem_analyzer.close()


# counting lemmas frequency for one document
def regular_lemmas(doc_id):
    lemmas_freq_doc(doc_id, status['lemmas'])


# counting lemmas frequency for one document
def lemmas_freq_doc(doc_id, new_status=0):
    lemmas = {}
    morpho = db.get_morpho(doc_id)
    for i in morpho:
        for l in i.get('analysis', []):
            if l.get('lex', False):
                if (not l['lex'] in stop_lemmas) & (l.get('wt', 0) > 0):
                    lemmas[l['lex']] = lemmas.get(l['lex'], 0) + l.get('wt', 1)
    db.put_lemmas(doc_id, lemmas, new_status)


# compute idf and object-features matrix for training set
# idf for calc features of new docs
# object-features for learning model
# doc_index links doc_id and row index in object-features
# lemma_index links lemmas and column index in object-features
def idf_object_features_set(set_id):
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

    # choose most important lemmas and add in overall list by giving index

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

    feat_max = np.sum(object_features, axis=0)
    print_lemmas(set_id, [k for k, v in enumerate(feat_max) if v == 0], lemma_index, idf)
    print(np.min(np.sum(object_features, axis=1)))
    # save to db: idf, indexes and object_features
    db.put_training_set_params(set_id, idf,  doc_index, lemma_index, object_features)

    # print(idf)
    # print(doc_index)
    # print(lemma_index)
    # print(object_features)


def sigmoid_array(x):
    for l in range(len(x)):
        x[l] = 1/(1 + math.exp(-x[l]))
    return x


def sigmoid(x):
    return 1/(1 + math.exp(-x))


# bigger value is worse
def entropy_difference(feature, answers, num_lemma):
    f_max = np.max(feature)
    f_min = np.min(feature)
    if f_max == f_min:
        print('lemma 0: ', num_lemma)
        return 10000
    step = (f_max - f_min) / 1000
    p = [[0, 0] for _ in range(1000)]
    sum_p = len(feature)
    for j in range(len(feature)):
        index = math.trunc((feature[j] - f_min)/step)
        if index == 1000:
            index = 999
        p[index][answers[j]] += 1
    result = 0
    for i in range(1000):
        if (p[i][0] != 0) & (p[i][1] != 0):
            result += math.log2((p[i][0] + p[i][1]) / sum_p) * (p[i][0] + p[i][1]) / sum_p - \
                      math.log2(p[i][0] / sum_p) * (p[i][0]) / sum_p - \
                      math.log2(p[i][1] / sum_p) * (p[i][1]) / sum_p
    return result


def print_lemmas(set_id, numbers, lemmas=None, idf=None):
    if idf is None:
        idf = {}
    if lemmas is None:
        lemmas = db.get_lemma_index(set_id)
    my_lemmas = [k for k in lemmas if lemmas[k] in numbers]
    print(numbers)
    print(my_lemmas)
    print([idf.get(k, '') for k in my_lemmas])
    # for i in numbers:
    #     m
    #     print(i, [k for k in lemmas if lemmas[k] == i])


def learning_rubric_model(set_id, rubric_id):

    # get answers for rubric
    answers = db.get_answers(set_id, rubric_id)
    # get object_features, lemma_index, doc_index
    doc_index, object_features = db.get_doc_index_object_features(set_id)

    print(np.min(np.sum(object_features, axis=0)))
    print(np.min(np.sum(object_features, axis=1)))

    doc_number = len(doc_index)
    # answers_index - answers by indexes, answers_array - array for compute cross_entropy in tensorflow
    answers_array = np.zeros((doc_number, 1))
    answers_index = np.zeros(doc_number, dtype=int)
    for doc_id in doc_index:
        answers_index[doc_index[doc_id]] = answers[doc_id]
        answers_array[doc_index[doc_id], 0] = answers[doc_id] * 2 - 1

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
        print_lemmas(set_id, good_numbers[0:30])
        print(feature_entropy[good_numbers[0:30]])
    else:
        for i in range(features_number):
            mif_indexes.append(i)

    x = tf.placeholder(tf.float32, shape=[None, mif_number])
    y_ = tf.placeholder(tf.float32, shape=[None, 1])
    w = tf.Variable(tf.truncated_normal([mif_number, 1], stddev=0.1))
    b = tf.Variable(0.00001)

    y = tf.matmul(x, w) + b
    # take probability (sigmoid) when answer is true and -sigmoid (instead 1-sigmoid) otherwise
    cross_entropy_array = tf.sigmoid(y) * y_
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
            if use_mif:
                sess.run(train_step, feed_dict={x: object_features[indexes[0:100], :][:,mif_indexes], y_: local_answers})
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
    db.put_model(rubric_id, set_id, model, mif_indexes, mif_number)

    # print(W.eval(sess))
    # print(b.eval(sess))


# regular ribrication
def regular_rubrication(doc_id):
    spot_doc_rubrics(doc_id, rubrics_for_regular, status['rubrics'])


# take 1 doc and few rubrics
# save in DB doc_id, rubric_id and YES or NO
# rubrics is a dict. key = rubric_id, value = None or set_id
# value = set_id: use model, learned with this trainingSet
def spot_doc_rubrics(doc_id, rubrics, new_status=0):
    # get lemmas by doc_id
    lemmas = db.get_lemmas(doc_id)
    # compute document size
    doc_size = 0
    for lemma in lemmas:
        doc_size += lemmas[lemma]
    # models for rubrics
    models = {}

    correct_answers = {}

    # fill set_id in rubrics and data in models
    for rubric_id in rubrics:
        correct_answers[rubric_id] = db.get_answer_doc(doc_id, rubric_id)
        if rubrics[rubric_id] is None:
            rubrics[rubric_id] = db.get_set_id_by_rubric_id(rubric_id)
        models[rubric_id] = db.get_model(rubric_id, rubrics[rubric_id])
    # get dict with idf and lemma_index for each set_id
    # sets[...] is dict: {'idf':..., 'lemma_index': ...}
    sets = db.get_idf_lemma_index_by_set_id(rubrics.values())
    for set_id in sets:
        # compute idf for doc_id (lemmas) and set_id
        idf_doc = {}
        for lemma in lemmas:
            idf_doc[lemma] = lemmas[lemma] * sets[set_id]['idf'].get(lemma, 0) / doc_size
        sets[set_id]['idf_doc'] = idf_doc
    # for each rubric
    answers = {}
    for rubric_id in rubrics:
        set_id = rubrics[rubric_id]
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
        answers[rubric_id] = {'result': round(probability), 'model_id': models[rubric_id]['model_id']}
        # if answers[rubric_id]['result'] == correct_answers[rubric_id]:
        #     res = 'correct'
        # else:
        #     res = 'incorrect'
        # print(doc_id, answers[rubric_id]['result'],  res)
    db.put_rubrics(doc_id, answers, new_status)


# compute TP, FP, TN, FN, Precision, Recall and F-score on data from db
def f1_score(model_id, test_set_id, rubric_id):
    result = {'true_positive': 0, 'false_positive': 0, 'true_negative': 0, 'false_negative': 0}
    # right answers
    answers = db.get_answers(test_set_id, rubric_id)
    # rubrication results
    rubrication_result = db.get_rubrication_result(model_id, test_set_id, rubric_id)

    for key in rubrication_result:
        if rubrication_result[key] == answers[key]:
            if rubrication_result[key] == 1:
                result['true_positive'] += 1
            else:
                result['true_negative'] += 1
        else:
            if rubrication_result[key] == 1:
                result['false_positive'] += 1
            else:
                result['false_negative'] += 1
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
    return result
