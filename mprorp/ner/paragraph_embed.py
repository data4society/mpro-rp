
import os
import getpass
import sys
import time

import numpy as np
import random
import collections
import tensorflow as tf
import math
import mprorp.ner.data_utils.utils as du
import mprorp.ner.data_utils.ner as ner
from mprorp.ner.utils import data_iterator, data_iterator2
from mprorp.ner.model import LanguageModel
import mprorp.analyzer.db as db
from mprorp.ner.config import features_size
from mprorp.ner.feature import ner_feature_types
import pickle as pickle
from mprorp.utils import home_dir
from mprorp.ner.saver import saver
# from gensim.models import word2vec
import mprorp.ner.feature as feature
import mprorp.ner.set_list as set_list


import mprorp.db.dbDriver as Driver
from mprorp.db.models import *


# set_docs = {}
# for cl in sets:
#     set_docs[cl] = {}
#     for set_type in sets[cl]:
#         set_docs[cl][set_type] = db.get_set_docs(sets[cl][set_type])
#         print(cl, set_type, len(set_docs[cl][set_type]), 'documents')

embedding_for_word_count = 5

verbose = True

consistent_words = True
use_par_embed = False
use_NN = False
learning_rate = 1

batch_size = 100
embedding_size = 128  # 128  # Dimension of the embedding vector.
# embed_par_size = 400
skip_window = 1  # How many words to consider left and right (if not consistent_words)
num_skips = 3  # Size of the window with consistent or random order words
l1_size = 512  # 256

reg_l1 = 0.0001
reg_emded = 0.00005
dropout = 0.7

print('embedding_for_word_count',embedding_for_word_count)

print('consistent_words', consistent_words)
print('use_par_embed', use_par_embed)
print('use_NN', use_NN)
print('learning_rate', learning_rate)

print('batch_size',batch_size)
print('embedding_size', embedding_size)
# embed_par_size = 400
print('skip_window', skip_window)
print('num_skips', num_skips)
print('l1_size', l1_size)

print('reg_l1', reg_l1)
print('reg_emded', reg_emded)
print('dropout', dropout)

# reg_softmax = 0.00005

# We pick a random validation set to sample nearest neighbors. here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = 10  # Random set of words to evaluate similarity on.
valid_window = 100  # Only pick dev samples in the head of the distribution.
valid_examples = np.array(random.sample(range(valid_window), valid_size))
num_sampled = 64  # Number of negative examples to sample.

valid_examples_p = [0, 1, 2, 3, 4]

data_index = 0
par_index = 0


def new_buffer(span, paragraphs):
    global data_index
    global par_index
    if data_index + span > len(paragraphs[par_index]):
        data_index = 0
        par_index = (par_index + 1) % len(paragraphs)
        while len(paragraphs[par_index]) < span:
            par_index = (par_index + 1) % len(paragraphs)
    buffer = collections.deque(maxlen=span)
    for _ in range(span):
        buffer.append(paragraphs[par_index][data_index])
        data_index += 1
    if data_index == len(paragraphs[par_index]):
        par_index = (par_index + 1) % len(paragraphs)
        data_index = 0
    return buffer


def generate_batch(batch_size, num_skips, skip_window, voc_size, paragraphs):
    global data_index
    global par_index
    global use_par_embed

    # assert batch_size % num_skips == 0
    # assert num_skips <= 2 * skip_window

    batch = np.ndarray(shape=(batch_size, num_skips + use_par_embed), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    if consistent_words:
        span = num_skips + 1  # [ skip_window target skip_window ]
    else:
        span = 2 * skip_window + 1  # [ skip_window target skip_window ]
    buffer = new_buffer(span, paragraphs)

    for i in range(batch_size):
        if not consistent_words:
            target = skip_window  # target label at the end of the buffer
            targets_to_avoid = [skip_window]
        for j in range(num_skips):
            if not consistent_words:
                while target in targets_to_avoid:
                    target = random.randint(0, span - 1)
                targets_to_avoid.append(target)
                batch[i, j] = buffer[target]
            else:
                batch[i, j] = buffer[j]
        if use_par_embed:
            batch[i, num_skips] = par_index + voc_size

        # print('buffer:', buffer)
        # print('labels:', labels)
        # print(buffer[num_skips])

        labels[i, 0] = buffer[num_skips]
        buffer.append(paragraphs[par_index][data_index])
        data_index += 1
        if data_index == len(paragraphs[par_index]):
            par_index = (par_index + 1) % len(paragraphs)
            data_index = 0
            buffer = new_buffer(span, paragraphs)
            # buffer.append(data[data_index])
            # data_index = (data_index + 1) % len(data)
    return batch, labels


def start():

    global num_skips
    global skip_window

    # training_set = [set_list.sets1250[0]]
    # training_set = [set_list.set_2['dev_160']]
    # training_set = [set_list.set34751]
    # training_set = [set_list.set_2['train_5120']]
    # training_set = [set_list.set_2['all_8323']]
    # training_set = '1b8f7501-c7a8-41dc-8b06-fda7d04461a2'
    # training_set = [set_list.set_2['dev_160'], set_list.set_2['dev_320']]
    training_set = set_list.sets1250[:5]
    # training_set = set_list.sets1250
    words_count = {}
    set_docs = []
    printed = False
    for tr_set_id in training_set:
        train_set_words = db.get_ner_feature(set_id=tr_set_id, feature='embedding')
        if verbose:
            print(len(train_set_words))
        for doc_id in train_set_words:
            if verbose and len(set_docs) % 1000 == 0:
                print('set_docs: ', len(set_docs))
            doc_words = train_set_words[doc_id]
            doc = []
            for element in doc_words:
                main_word = ''
                rate = 0
                for word in element[2]:
                    if rate < element[2][word]:
                        rate = element[2][word]
                        main_word = word
                doc.append(main_word)
                if main_word in words_count:
                    words_count[main_word] += 1
                else:
                    words_count[main_word] = 1
            set_docs.append(doc)
            if verbose and not printed:
                print(doc_words)
                print(doc)
                printed = True
    if verbose:
        print('set_docs - ok')
    train_set_words = None
    words_order = sorted(words_count.items(), key=lambda x: -x[1])
    if verbose:
        print('Most common words (+UNK)', words_order[:5])

    dictionary = []
    for word in words_order:
        if words_count[word[0]] > embedding_for_word_count:
            dictionary.append(word[0])

    if verbose:
        print(dictionary[:5])

    reverse_dictionary = {dictionary[i]: i for i in range(len(dictionary))}
    unk_word = len(dictionary)
    dictionary.append('UNKN')
    no_word = unk_word + 1
    dictionary.append('EMPTY')

    paragraphs = []
    total_words = 0
    for doc in set_docs:
        par_words = [no_word for i in range(num_skips)]# В начало параграфа добавим полное окно путсых слов
        for word in doc:
            par_words.append(reverse_dictionary[word] if word in reverse_dictionary else unk_word)
        total_words += len(par_words)
        paragraphs.append(par_words)

    vocabulary_size = len(reverse_dictionary) + 2
    paragraph_amount = len(paragraphs)
    if verbose:
        print('vocabulary_size:', vocabulary_size)

    if verbose:
        print('paragraphs:', [dictionary[di] for di in paragraphs[100][:20]])

        for num_skips, skip_window in [(2, 1), (4, 2)]:
            data_index = 0
            batch, labels = generate_batch(batch_size=8, num_skips=num_skips, skip_window=skip_window,
                                           voc_size=vocabulary_size, paragraphs=paragraphs)
            print('\nwith num_skips = %d and skip_window = %d:' % (num_skips, skip_window))
            print('    batch:', [dictionary[bii] if bii < vocabulary_size else bii for bi in batch for bii in bi])
            print('    labels:', [dictionary[li] for li in labels.reshape(8)])

    graph = tf.Graph()

    with graph.as_default(), tf.device('/cpu:0'):
        # Input data.
        features_number = num_skips + use_par_embed
        train_dataset = tf.placeholder(tf.int32, shape=[batch_size, features_number])
        train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
        valid_dataset = tf.constant(valid_examples, dtype=tf.int32)
        valid_dataset_p = tf.constant(valid_examples_p, dtype=tf.int32)

        # Variables.
        input_vector_size = embedding_size * num_skips if not use_par_embed else embedding_size * (num_skips + 1)
        embed_amount = vocabulary_size if not use_par_embed else vocabulary_size + paragraph_amount

        embeddings = tf.Variable(
                tf.random_uniform([embed_amount, embedding_size], -1.0, 1.0))

        if use_NN:
            weights_l1 = tf.Variable(
                tf.truncated_normal([input_vector_size, l1_size],
                                    stddev=1.0 / math.sqrt(embedding_size)))
            tf.add_to_collection('total_loss', 0.5 * reg_l1 * tf.nn.l2_loss(weights_l1))

            biases_l1 = tf.Variable(tf.zeros([l1_size]))
            softmax_matrix_dim = l1_size
        else:
            softmax_matrix_dim = input_vector_size

        softmax_weights = tf.Variable(
            tf.truncated_normal([vocabulary_size, softmax_matrix_dim],
                                stddev=1.0 / math.sqrt(embedding_size)))
        # tf.add_to_collection('total_loss', 0.5 * reg_softmax * tf.nn.l2_loss(softmax_weights))

        softmax_biases = tf.Variable(tf.zeros([vocabulary_size]))

        # Model.
        # Look up embeddings for inputs.
        embed = tf.nn.embedding_lookup(embeddings, train_dataset)
        embed = tf.reshape(
            embed, [-1, input_vector_size])
        tf.add_to_collection('total_loss', 0.5 * reg_emded * tf.nn.l2_loss(embed))
        # Compute the softmax loss, using a sample of the negative labels each time.
        if use_NN:
            h = tf.nn.tanh(tf.matmul(embed, weights_l1) + biases_l1)
            h_drop = tf.nn.dropout(h, dropout)
            cross_entropy = tf.reduce_mean(
                tf.nn.sampled_softmax_loss(weights=softmax_weights, biases=softmax_biases, inputs=h_drop,
                                           labels=train_labels, num_sampled=num_sampled, num_classes=vocabulary_size))
        else:
            cross_entropy = tf.reduce_mean(
                tf.nn.sampled_softmax_loss(weights=softmax_weights, biases=softmax_biases, inputs=embed,
                                           labels=train_labels, num_sampled=num_sampled, num_classes=vocabulary_size))

        tf.add_to_collection('total_loss', cross_entropy)
        loss = tf.add_n(tf.get_collection('total_loss'))

        # Optimizer.
        # Note: The optimizer will optimize the softmax_weights AND the embeddings.
        # This is because the embeddings are defined as a variable quantity and the
        # optimizer's `minimize` method will by default modify all variable quantities
        # that contribute to the tensor it is passed.
        # See docs on `tf.train.Optimizer.minimize()` for more details.
        optimizer = tf.train.AdagradOptimizer(learning_rate).minimize(loss)

        # Compute the similarity between minibatch examples and all embeddings.
        # We use the cosine distance:
        norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
        normalized_embeddings = embeddings / norm
        valid_embeddings = tf.nn.embedding_lookup(
            normalized_embeddings, valid_dataset)
        similarity = tf.matmul(valid_embeddings, tf.transpose(normalized_embeddings))
        valid_embeddings_p = tf.nn.embedding_lookup(
            normalized_embeddings, valid_dataset_p)
        similarity_p = tf.matmul(valid_embeddings_p, tf.transpose(normalized_embeddings))
        init = tf.initialize_all_variables()

    num_steps = 4001

    with tf.Session(graph=graph) as session:
        # tf.global_variables_initializer().run()
        session.run(init)
        print('Initialized')
        average_loss = 0
        for step in range(num_steps):
            batch_data, batch_labels = generate_batch(
                batch_size, num_skips, skip_window, vocabulary_size, paragraphs)
            feed_dict = {train_dataset : batch_data, train_labels : batch_labels}
            _, l = session.run([optimizer, loss], feed_dict=feed_dict)
            average_loss += l
            if step % 2000 == 0:
                if step > 0:
                    average_loss = average_loss / 2000
                # The average loss is an estimate of the loss over the last 2000 batches.
                print('Average loss at step %d: %f' % (step, average_loss))
                average_loss = 0
            # note that this is expensive (~20% slowdown if computed every 500 steps)
            if verbose:
                if step % 10000 == 0:
                    sim = similarity.eval()
                    for i in range(valid_size):
                        valid_word = dictionary[valid_examples[i]]
                        top_k = 8 # number of nearest neighbors
                        nearest = (-sim[i, :]).argsort()[1:top_k+1]
                        log = 'Nearest to %s:' % valid_word
                        for k in range(top_k):
                            close_word = dictionary[nearest[k]] if nearest[k] < vocabulary_size else nearest[k] - vocabulary_size
                            log = '%s %s (%s),' % (log, close_word, sim[i, nearest[k]])
                        print(log)
        interesting_pars = {}
        sim = similarity.eval()
        for i in range(valid_size):
            valid_word = dictionary[valid_examples[i]]
            top_k = 8  # number of nearest neighbors
            nearest = (-sim[i, :]).argsort()[1:top_k + 1]
            log = 'Nearest to %s:' % valid_word
            for k in range(top_k):
                close_word = dictionary[nearest[k]] if nearest[k] < vocabulary_size else nearest[k] - vocabulary_size
                log = '%s %s (%s),' % (log, close_word, sim[i, nearest[k]])
                if nearest[k] >= vocabulary_size:
                    interesting_pars[nearest[k] - vocabulary_size] = ''
            print(log)
        sim_p = similarity_p.eval()
        for i in range(len(valid_examples_p)):
            nearest = (-sim_p[i, :]).argsort()[1:top_k + 1]
            print('Nearest to ')
            print([dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])
            print('IS')
            for k in range(top_k):
                if nearest[k] < vocabulary_size:
                    print(sim_p[i,nearest[k]], dictionary[nearest[k]])
                else:
                    print(sim_p[i,nearest[k]], [dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])

        if verbose:
            for par in interesting_pars:
                print(par)
                print([dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])

        final_embeddings = normalized_embeddings.eval()


def start2():
    training_set = '1b8f7501-c7a8-41dc-8b06-fda7d04461a2'
    tr_set = db.get_set_docs(training_set)
    print(len(tr_set))
    print(tr_set)
    session = Driver.db_session()
    all_words = session.query(NERFeature).filter(
        NERFeature.doc_id.in_(tr_set) & (NERFeature.feature == 'embedding')).order_by(
        NERFeature.sentence_index, NERFeature.word_index).all()
    print('aii_words', len(all_words))

start()


