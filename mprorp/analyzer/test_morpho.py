import mprorp.analyzer.db as db
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import math
import tensorflow as tf


doc_id_1 = "7a721274-151a-4250-bb01-4a4772557d09"
doc_id_2 = "672f361d-1632-41b0-82de-dd8c85745063"

# one document morphological analysis
def morpho(id):
    m = Mystem(disambiguation=False)
    text = db.get_doc(id)
    print(text)
    new_morpho = m.analyze(text)
    db.put_morpho(id, new_morpho)

# counting lemmas frequently for one document
def lemmas_freq(id):
    lemmas = {}
    morpho = db.get_morpho(id)
    print('get_morpho: ', morpho)
    for i in morpho:
        for l in i.get('analysis',[]):
            if l.get('lex',False):
                lemmas[l['lex']] = lemmas.get(l['lex'], 0) + l.get('wt', 1)
    db.put_lemmas(id,lemmas)

# compute idf and object-features matrix for training set
# idf for calc features of new docs
# object-features for learning model
# doc_index links doc_id and row index in object-features
# lemma_index links lemmas and column index in object-features
def idf_learn( set_id = ''):
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

    print(idf)
    print(doc_index)
    print(lemma_index)
    print(object_features)

def learning_rubric_model(set_id, rubric_id):

    answers = db.get_answers(set_id, rubric_id)
    doc_index, object_features = db.get_doc_index_object_features(set_id)

    for doc_id in answers:
        print(answers[doc_id])
    print(doc_index)
    print(object_features[0])
    return

    #lerning model
    #get object_features, lemma_index, doc_index
    #get answers for rubric
    answers = {doc_id_1: 0, doc_id_2: 1}

    doc_number = doc_counter
    lemma_number = lemma_counter

    answers_array = np.zeros((doc_number, 1))
    answers_array[1, 0] = 1
    for doc_id in doc_index:
        answers_array[doc_index[doc_id], 0] = answers[doc_id] * 2 - 1

    x = tf.placeholder(tf.float32, shape=[None, lemma_number])
    y_ = tf.placeholder(tf.float32, shape=[None, 1])
    W = tf.Variable(tf.zeros([lemma_number, 1]))
    b = tf.Variable(0.01)

    y = tf.matmul(x,W) + b
    cross_entropy = - tf.reduce_mean(tf.sigmoid(y) * y_)

    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)
    init = tf.initialize_all_variables()

    sess = tf.Session()
    sess.run(init)

    for i in range(300):
        sess.run(train_step, feed_dict={x: object_features, y_: answers_array})

    print(W.eval(sess))
    print(b.eval(sess))
    #print(sess.run(accuracy, feed_dict={x: object_features, y_:answers_array}))

#set_id_1 = db.put_training_set([doc_id_1, doc_id_2])
#print(set_id_1)

set_id = "1dcc4dc5-a706-4e61-8b37-26b5fd554145"

#for doc_id in db.get_set_docs(set_id):
#    morpho(doc_id)
#    lemmas_freq(doc_id)

#idf_learn(set_id)

rubric_id = '693a9b39-cb8e-4525-9333-1dadcda7c34e'
learning_rubric_model(set_id, rubric_id)
