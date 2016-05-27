import mprorp.analyzer.db as db
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import math
import tensorflow as tf


doc_id_1 = "7a721274-151a-4250-bb01-4a4772557d09"
doc_id_2 = "672f361d-1632-41b0-82de-dd8c85745063"

# one document morphological analysis
def morpho_doc(doc_id):
    #mystem_analyzer = Mystem(disambiguation=False)
    text = db.get_doc(doc_id)
    #print(text)
    mystem_analyzer.start()
    new_morpho = mystem_analyzer.analyze(text)
    #print(new_morpho)
    db.put_morpho(doc_id, new_morpho)
    mystem_analyzer.close()

# counting lemmas frequency for one document
def lemmas_freq_doc(doc_id):
    lemmas = {}
    morpho = db.get_morpho(doc_id)
    for i in morpho:
        for l in i.get('analysis',[]):
            if l.get('lex',False):
                lemmas[l['lex']] = lemmas.get(l['lex'], 0) + l.get('wt', 1)
    db.put_lemmas(doc_id, lemmas)

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
    #number of lemmas in document
    doc_size = {}
    #index of lemma in overall list
    lemma_index = {}
    #lemma counter in overall list
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
                object_features[doc_index[doc_id],lemma_index[lemma]] = doc_lemmas[lemma] / doc_size[doc_id] * idf[lemma]

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

def learning_rubric_model(set_id, rubric_id):

    # get answers for rubric
    answers = db.get_answers(set_id, rubric_id)
    #print(answers)
    # get object_features, lemma_index, doc_index
    doc_index, object_features = db.get_doc_index_object_features(set_id)

    #print(doc_index)
    #print(object_features)
    doc_number = len(doc_index)
    # if we know answers, we can select most important features (mif):
    # mif[k] = l:
    # feature k from object_features is used in position l, if l >= 0
    # if feature k ins not most important, l = -1
    features_number = len(object_features[0])
    mif = np.zeros(features_number)
    for i in range(features_number):
        mif[i] = i

    #take probability (sigmoid) when answer is true and -sigmoid (instead 1-sigmoid) otherwise
    answers_array = np.zeros((doc_number, 1))
    for doc_id in doc_index:
        answers_array[doc_index[doc_id], 0] = answers[doc_id] * 2 - 1

    for doc_id in doc_index:
        print(db.get_doc(doc_id))
        index = doc_index[doc_id]
        print(answers_array[index,:])
        print(object_features[index])

    x = tf.placeholder(tf.float32, shape=[None, features_number])
    y_ = tf.placeholder(tf.float32, shape=[None, 1])
    W = tf.Variable(tf.truncated_normal([features_number, 1],stddev=0.1)) #tf.truncated_normal(shape, stddev=0.1)
    b = tf.Variable(0.00001)

    y = tf.matmul(x,W) + b
    cross_entropy = - tf.reduce_mean(tf.sigmoid(y) * y_)

    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
    init = tf.initialize_all_variables()

    sess = tf.Session()
    sess.run(init)

    for i in range(5000):
        sess.run(train_step, feed_dict={x: object_features, y_: answers_array})
        #my_W = W.eval(sess)
        #my_b = b.eval(sess)
        #print(i, (sigmoid(np.dot(np.asarray(object_features), my_W) + my_b) * np.asarray(answers_array)))

    model = W.eval(sess)[:,0]
    model = model.tolist()
    model.append(float(b.eval(sess)))
    myvar = float(b.eval(sess))
    #print(type(model[0]), type(myvar))
 #   print(model)
    db.put_model(rubric_id, set_id, model, mif, features_number)

    #print(W.eval(sess))
    #print(b.eval(sess))
    #print(answers_array)
    #print(type(my_W))
    # print(np.dot(np.asarray(object_features),my_W) + my_b)
    #print(sess.run(accuracy, feed_dict={x: object_features, y_:answers_array}))

# take 1 doc and few rubrics
# save in DB doc_id, rubric_id and YES or NO
# rubrics is a dict. key = rubric_id, value = None or set_id
# value = set_id: use model, learned with this trainingSet
def spot_doc_rubrics(doc_id, rubrics):
    # get lemmas by doc_id
    lemmas = db.get_lemmas(doc_id)
    # compute document size
    doc_size = 0
    for lemma in lemmas:
        doc_size += lemmas[lemma]
    #models for rubrics
    models = {}

    # fill set_id in rubrics and data in models
    for rubric_id in rubrics:
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
        features_num = models[rubric_id]['features_num']
        features_array = np.array([0 for i in range(features_num + 1)])
        lemma_index = sets[set_id]['lemma_index']
        for lemma in lemmas:
            # lemma index in lemmas of set
            ind_lemma = lemma_index.get(lemma, -1)
            # if lemma from doc is in lemmas for training set
            if ind_lemma > -1:
                index = models[rubric_id]['features'][ind_lemma]
                if index > -1:
                    #print(index, len(features_array))
                    #print(features_array[index] )
                    #print(sets[set_id]['idf_doc'][lemma])
                    features_array[index] = sets[set_id]['idf_doc'][lemma]
        features_array[features_num] = 1
        #print(models[rubric_id]['model'])
        probability = sigmoid(np.dot(features_array, models[rubric_id]['model']))
        answers[rubric_id] = {'result':round(probability), 'model_id':models[rubric_id]['model_id']}
    db.put_rubrics(doc_id, answers)
    print(doc_id, answers)


mystem_analyzer = Mystem(disambiguation=False)
