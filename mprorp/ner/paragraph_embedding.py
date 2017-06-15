
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
import mprorp.ner.feature as ner_feature
import mprorp.analyzer.rubricator as rb

import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from mprorp.config.settings import learning_parameters as lp

# set_docs = {}
# for cl in sets:
#     set_docs[cl] = {}
#     for set_type in sets[cl]:
#         set_docs[cl][set_type] = db.get_set_docs(sets[cl][set_type])
#         print(cl, set_type, len(set_docs[cl][set_type]), 'documents')


models_and_set = lp['models and sets']
rubric_num = models_and_set['rubric_num']
train_set_name = models_and_set['train_set_name']
training_set = set_list.sets[rubric_num][train_set_name]

embedding_id = models_and_set['embedding_id']

params = lp['paragraph embeddings']
embedding_for_word_count = params['embedding_for_word_count'] # 5
learning_steps = params['learning_steps']
calc_steps = params['calc_steps']

verbose = params['verbose'] # True

params_consistent_words = params['consistent_words'] # True
use_par_embed = params['use_par_embed'] # True
use_NN = params['use_NN'] # True
learning_rate = params['learning_rate'] # 1

params_batch_size = params['batch_size'] # 100
params_embedding_size = params['embedding_size'] # 128  # 128  # Dimension of the embedding vector.
# embed_par_size = 400
params_skip_window = params['skip_window'] # 1  # How many words to consider left and right (if not consistent_words)
params_num_skips = params['num_skips'] # 3  # Size of the window with consistent or random order words
params_l1_size = params['l1_size'] # 512  # 256

reg_l1 = params['reg_l1'] # 0.0001
reg_emded = params['reg_emded'] # 0.00005
dropout = params['dropout'] # 0.7

if use_NN:
    filename = params['filename_NN'] # 'ModelEP_0406_128_NonCons_6_3.pic'
else:
    filename = params['filename_no_NN'] # 'ModelEP_0406_128_NonCons_6_3.pic'

# parameters for rubrication
reg_coef = params['reg_coef'] # 0.000005
lr=params['lr'] # 0.0025
tf_steps = params['tf_steps'] # 100000

print('embedding_for_word_count', embedding_for_word_count)

print('consistent_words', params_consistent_words)
print('use_par_embed', use_par_embed)
print('use_NN', use_NN)
print('learning_rate', learning_rate)

print('batch_size',params_batch_size)
print('embedding_size', params_embedding_size)
# embed_par_size = 400
print('skip_window', params_skip_window)
print('num_skips', params_num_skips)
print('l1_size', params_l1_size)

print('reg_l1', reg_l1)
print('reg_emded', reg_emded)
print('dropout', dropout)

# reg_softmax = 0.00005

# We pick a random validation set to sample nearest neighbors. here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = params['valid_size']  # 10  # Random set of words to evaluate similarity on.
valid_window = params['valid_window']  #100  # Only pick dev samples in the head of the distribution.
valid_examples = np.array(random.sample(range(valid_window), valid_size))
num_sampled = params['num_sampled']  # 64  # Number of negative examples to sample.

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


def generate_batch(batch_size, num_skips, skip_window, consistent_words, voc_size, paragraphs):
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


def append_doc_words(doc_list, set_docs, new_dictionary, words_count, doc_ids):

    train_set_words = db.get_ner_feature(doc_id_list=doc_list, feature='embedding')
    if verbose:
        print('doc_list', len(doc_list))
        print('train_set_words', len(train_set_words))
    for doc_id in train_set_words:
        if doc_id in doc_ids:
            print('skip doc ', doc_id, ' длина doc_ids ', len(doc_ids))
            continue
        # if verbose and len(set_docs) % 1000 == 0:
        #     print('set_docs: ', len(set_docs))
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
            if new_dictionary:
                if main_word in words_count:
                    words_count[main_word] += 1
                else:
                    words_count[main_word] = 1
        set_docs.append(doc)
        doc_ids.append(doc_id)


def fill_paragraphs_for_learning(training_set, num_skips, doc_id=None, dictionary=None, reverse_dictionary=None, verbose=False):

    new_dictionary = dictionary is None

    paragraphs = []
    words_count = {}
    set_docs = []
    doc_ids=[]

    if doc_id is None:
        train_set_docs = [str(i) for i in db.get_set_docs(training_set)]
    else:
        train_set_docs = [doc_id]
    start_doc = 0
    while len(train_set_docs) - start_doc > 2000:
        append_doc_words(train_set_docs[start_doc: start_doc + 1250], set_docs, new_dictionary, words_count, doc_ids)
        start_doc += 1250
    append_doc_words(train_set_docs[start_doc:], set_docs, new_dictionary, words_count, doc_ids)

    if verbose:
        print('set_docs - ok')
    if new_dictionary:
        dictionary = []
        reverse_dictionary = {}
        words_order = sorted(words_count.items(), key=lambda x: -x[1])
        if verbose:
            print('Most common words (+UNK)', words_order[:5])

        for word in words_order:
            if words_count[word[0]] > embedding_for_word_count:
                dictionary.append(word[0])

        if verbose:
            print(dictionary[:5])

        unk_word = len(dictionary)
        dictionary.append('UNKN')
        no_word = unk_word + 1
        dictionary.append('EMPTY')
        for i in range(len(dictionary)):
            reverse_dictionary[dictionary[i]] = i
    else:
        unk_word = reverse_dictionary['UNKN']
        no_word = reverse_dictionary['EMPTY']

    total_words = 0

    for doc in set_docs:
        par_words = [no_word for i in range(num_skips)]# В начало параграфа добавим полное окно путсых слов
        for word in doc:
            par_words.append(reverse_dictionary[word] if word in reverse_dictionary else unk_word)
        total_words += len(par_words)
        paragraphs.append(par_words)

    if new_dictionary:
        return paragraphs, doc_ids, dictionary, reverse_dictionary
    else:
        return paragraphs, doc_ids, None, None


def run_model(learning, num_steps, filename=None, model_params=None):

    global data_index

    assert use_par_embed or learning  #If we use existed model (learning=False), use_par_embed must be True

    if learning:
        dictionary = model_params['word_list']
    reverse_dictionary = model_params['dict']
    paragraphs = model_params['paragraphs']
    doc_ids = model_params['doc_ids']
    l1_size = model_params['params']['l1_size']
    embedding_size = model_params['params']['embedding_size']
    num_skips = model_params['params']['num_skips']
    skip_window = model_params['params']['skip_window']
    consistent_words = model_params['params']['consistent_words']
    batch_size = model_params['params']['batch_size']
    vocabulary_size = len(reverse_dictionary) + 2
    paragraph_amount = len(paragraphs)
    if verbose:
        print('vocabulary_size:', vocabulary_size)

    if verbose and learning:
        print('paragraphs:', [dictionary[di] for di in paragraphs[0][:20]])

        for num_skips_loc, skip_window_loc in [(2, 1), (4, 2)]:
            data_index = 0
            batch, labels = generate_batch(batch_size=8, num_skips=num_skips_loc, skip_window=skip_window_loc,
                                           consistent_words=consistent_words, voc_size=vocabulary_size,
                                           paragraphs=paragraphs)
            print('\nwith num_skips = %d and skip_window = %d:' % (num_skips_loc, skip_window_loc))
            print('    batch:', [dictionary[bii] if bii < vocabulary_size else bii for bi in batch for bii in bi])
            print('    labels:', [dictionary[li] for li in labels.reshape(8)])
    #
    # if not learning:
    #     with open(home_dir + '/weights' + filename, 'rb') as f:
    #         model_params = pickle.load(f)

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
        # embed_amount = vocabulary_size if not use_par_embed else vocabulary_size + paragraph_amount

        # embeddings = tf.Variable(
        #     tf.random_uniform([embed_amount, embedding_size], -1.0, 1.0))

        if use_par_embed:
            if learning:
                embeddings_w = tf.Variable(
                        tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0), trainable=learning)
            else:
                embeddings_w = tf.Variable(model_params['embed'], trainable=False)
            embeddings_p = tf.Variable(
                    tf.random_uniform([paragraph_amount, embedding_size], -1.0, 1.0))
            embeddings = tf.concat(0, [embeddings_w, embeddings_p])
        else:
            embeddings = tf.Variable(
                tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))

        if use_NN:
            if learning:
                weights_l1 = tf.Variable(
                    tf.truncated_normal([input_vector_size, l1_size],
                                        stddev=1.0 / math.sqrt(embedding_size)))
                tf.add_to_collection('total_loss', 0.5 * reg_l1 * tf.nn.l2_loss(weights_l1))

                biases_l1 = tf.Variable(tf.zeros([l1_size]))
            else:
                weights_l1 = tf.Variable(model_params['weights_l1'], trainable=False)
                biases_l1 = tf.Variable(model_params['biases_l1'], trainable=False)
            softmax_matrix_dim = l1_size
        else:
            softmax_matrix_dim = input_vector_size

        if learning:
            softmax_weights = tf.Variable(
                tf.truncated_normal([vocabulary_size, softmax_matrix_dim],
                                    stddev=1.0 / math.sqrt(embedding_size)))
            # tf.add_to_collection('total_loss', 0.5 * reg_softmax * tf.nn.l2_loss(softmax_weights))
            softmax_biases = tf.Variable(tf.zeros([vocabulary_size]))
        else:
            softmax_weights = tf.Variable(model_params['softmax_weights'], trainable=False)
            # tf.add_to_collection('total_loss', 0.5 * reg_softmax * tf.nn.l2_loss(softmax_weights))
            softmax_biases = tf.Variable(model_params['softmax_biases'], trainable=False)



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

        if learning:
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

    with tf.Session(graph=graph) as session:
        # tf.global_variables_initializer().run()
        session.run(init)
        print('Initialized')
        average_loss = 0
        for step in range(num_steps):
            batch_data, batch_labels = generate_batch(
                batch_size, num_skips, skip_window, consistent_words, vocabulary_size, paragraphs)
            feed_dict = {train_dataset : batch_data, train_labels : batch_labels}
            _, l = session.run([optimizer, loss], feed_dict=feed_dict)
            average_loss += l
            if learning:
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
        # ---------- save model ----------------
        if learning:
            embed_for_save = embeddings.eval()[:vocabulary_size, :]
            # embed_for_save_list = embed_for_save.tolist()
            # print(type(embed_for_save_list), type(embed_for_save_list[0]), len(embed_for_save_list.shape), embed_for_save_list[:3, :3])
            params_for_save = {
                'consistent_words': consistent_words,
                'embedding_size': embedding_size,
                'skip_window': skip_window,
                'num_skips': num_skips,
                'l1_size': l1_size
                # 'batch_size': batch_size
            }
            for_save = {
                'params': params_for_save,
                'embed': embed_for_save,
                'softmax_weights': softmax_weights.eval(),
                'softmax_biases': softmax_biases.eval(),
                'dict': reverse_dictionary,
                'word_list': dictionary
            }
            if use_NN:
                for_save['weights_l1'] = weights_l1.eval()
                for_save['biases_l1'] = biases_l1.eval()
            with open(home_dir + '/weights' + filename, 'wb') as f:
                pickle.dump(for_save, f)
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
            doc_txt = {}
            for i in range(len(valid_examples_p)):
                nearest = (-sim_p[i, :]).argsort()[1:top_k + 1]
                print('Nearest to ')
                if doc_txt.get(doc_ids[i], None) is None:
                    doc_txt[doc_ids[i]] = db.get_doc_text(doc_ids[i])
                print(doc_txt[doc_ids[i]])
                print('---------------------------------===================================--------------------------------------')
                # print([dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])
                print('IS')
                for k in range(top_k):
                    if nearest[k] < vocabulary_size:
                        print(sim_p[i,nearest[k]], dictionary[nearest[k]])
                        print('---------------------------------===================================--------------------------------------')
                    else:
                        doc_id = doc_ids[nearest[k] - vocabulary_size]
                        if doc_txt.get(doc_id, None) is None:
                            doc_txt[doc_id] = db.get_doc_text(doc_id)
                        print(sim_p[i,nearest[k]], doc_txt[doc_id])
                        print('---------------------------------===================================--------------------------------------')
                        # print(sim_p[i,nearest[k]], [dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])
            if verbose:
                for par in interesting_pars:
                    print(par)
                    if doc_txt.get(doc_ids[par], None) is None:
                        doc_txt[doc_ids[par]] = db.get_doc_text(doc_ids[par])
                    print(doc_txt[doc_ids[par]])
                    print('---------------------------------===================================--------------------------------------')
                    # print([dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])

        if learning:
            return None
        else:
            return embeddings_p.eval()


def create_word_emb(my_sets, just_new=False):
    docs = set()
    for s in my_sets:
        docs.update(set(db.get_set_docs(s)))
    print(len(docs))
    docs_list = [str(i) for i in docs]
    print(docs_list[0])
    docs_str = set(docs_list)
    count = 0
    if just_new:
        old_docs = db.get_ner_feature(doc_id_list=list(docs), feature='embedding')
        old_docs_list = [str(i) for i in old_docs.keys()]
        print(old_docs_list[0])
        docs_str.difference_update(set(old_docs_list))
        print(len(docs_str))

    for doc_id in docs_str:
        rb.morpho_doc2(str(doc_id))
        rb.lemmas_freq_doc2(str(doc_id))
        ner_feature.create_embedding_feature2(str(doc_id))
        count += 1
        if count % 10 == 0:
            print(str(count) + " of " + str(len(docs)))


def start_prepare_docs(just_new=False):
    paragraph_set = []
    # for ind in ['11', '12', '13', '14', '15', '16']:
    #     paragraph_set.append(set_list.sets[ind]['tr_set_2'])
    #     paragraph_set.append(set_list.sets[ind]['test_set_2'])
    for ind in ['pp', 'ss']:
        paragraph_set.append(set_list.sets[ind]['train_set_2'])
        paragraph_set.append(set_list.sets[ind]['test_set_2'])
    create_word_emb(paragraph_set, just_new)


def model_emb_par_teach_or_calc(teach=True):

    #Learning model

    # training_set = [set_list.sets1250[0]]
    # training_set = [set_list.set_2['dev_160']]
    # training_set = [set_list.set34751]
    # training_set = [set_list.set_2['train_5120']]
    # training_set = [set_list.set_2['all_8323']]
    # training_set = '1b8f7501-c7a8-41dc-8b06-fda7d04461a2'
    # training_set = [set_list.set_2['dev_160'], set_list.set_2['dev_320']]
    # training_set = set_list.sets1250[:5]
    # training_set = set_list.sets1250

    if teach:
        paragraphs, doc_ids, word_list, reverse_dictionary = fill_paragraphs_for_learning(training_set, params_num_skips, verbose=verbose)
        if verbose:
            print('learning start')
        model_params = dict()
        model_params['word_list'] = word_list
        model_params['dict'] = reverse_dictionary
        model_params['paragraphs'] = paragraphs
        model_params['doc_ids'] = doc_ids
        model_params['params'] = {
            'l1_size': params_l1_size,
            'embedding_size': params_embedding_size,
            'skip_window': params_skip_window,
            'num_skips': params_num_skips,
            'batch_size': params_batch_size,
            'consistent_words': params_consistent_words
        }
        run_model(True, learning_steps, filename=filename, model_params=model_params)
    else:

        #Learninng embeddings

        paragraph_set = []

        # for ind in ['11']:
        # for ind in ['11', '12', '13', '14', '15', '16']:
        #     paragraph_set.append(set_list.sets[ind]['tr_set_2'])
        #     paragraph_set.append(set_list.sets[ind]['test_set_2'])
        for ind in ['pp']:
            paragraph_set.append(set_list.sets[ind]['test_set_0'])
        #     paragraph_set.append(set_list.sets[ind]['test_set'])
        # print(training_set, paragraph_set)
        with open(home_dir + '/weights' + filename, 'rb') as f:
            model_params = pickle.load(f)

        if verbose:
            print('fill paragraphs start')
        paragraphs, doc_ids, _, _ = fill_paragraphs_for_learning(paragraph_set,
                                                                 model_params['params']['num_skips'],
                                                                 dictionary=model_params['word_list'],
                                                                 reverse_dictionary=model_params['dict'],
                                                                 verbose=verbose)
        if verbose:
            print('calc embeddings start')
            print('paragraphs: ', len(paragraphs))
            print('doc_ids: ', len(doc_ids))
        model_params['paragraphs'] = paragraphs
        model_params['doc_ids'] = doc_ids
        model_params['params']['batch_size'] = params_batch_size
        em_p = run_model(False, calc_steps, model_params=model_params)
        if len(filename) > 40:
            print('Length of filename must be less or equal 40')
            exit()
        session = Driver.db_session()
        if verbose:
            print('delete old embedding start')
        embeds = session.query(Embedding).filter(Embedding.emb_id == filename).all()
        if embeds is None or len(embeds) == 0:
            new_emb = Embedding(emb_id=filename, name='Embedding for docs built by model from ' + filename)
            session.add(new_emb)
        else:
            new_emb = embeds[0]
        for i in range(len(doc_ids)):
            vec = em_p[i, :].tolist()
            session.query(DocEmbedding).filter(
                (DocEmbedding.doc_id == doc_ids[i]) & (DocEmbedding.embedding == new_emb.emb_id)).delete()
            new_vec = DocEmbedding(doc_id=doc_ids[i], embedding=new_emb.emb_id, vector=vec)
            session.add(new_vec)
        session.commit()


def calc_paragraph_embedding2(doc_id):
    """wrap for spot_doc_rubrics with local session"""
    db.doc_apply(doc_id, calc_paragraph_embedding)


def calc_paragraph_embedding(doc, session=None, commit_session=True):
    if session is None:
        session = Driver.db_session()
    with open(home_dir + '/weights' + filename, 'rb') as f:
        model_params = pickle.load(f)
    paragraphs, doc_ids, _, _ = fill_paragraphs_for_learning(None,
                                                             model_params['params']['num_skips'],
                                                             doc_id=doc.doc_id,
                                                             dictionary=model_params['word_list'],
                                                             reverse_dictionary=model_params['dict'],
                                                             verbose=verbose)
    model_params['paragraphs'] = paragraphs
    model_params['doc_ids'] = doc_ids
    model_params['params']['batch_size'] = len(paragraphs[0]) - 2*model_params['params']['num_skips']
    em_p = run_model(False, calc_steps, model_params=model_params)

    vec = em_p[0, :].tolist()
    emb_id = embedding_id  # нужно брать из файла с параметрами, а ту
    session.query(DocEmbedding).filter(
        (DocEmbedding.doc_id == doc.doc_id) & (DocEmbedding.embedding == emb_id)).delete()
    new_vec = DocEmbedding(doc_id=doc.doc_id, embedding=emb_id, vector=vec)
    session.add(new_vec)
    if commit_session:
        session.commit()


def create_rubric_train_data(tr_set, rubric_id, embedding_id, add_tf_idf=False, verbose=False):
    if verbose:
        print('start read embedding')
    embeds = db.get_docs_embedding(embedding_id, tr_set)
    # doc_ids = []
    emb_list = []
    ans_list = []
    if verbose:
        print('start read answers')
    answers = db.get_rubric_answers(tr_set, rubric_id)
    mif_indexes = None
    if add_tf_idf:
        if verbose:
            print('start read tf-idf data')
        mif_indexes, doc_index, tf_idf_features = rb.create_train_data_tf_idf(tr_set, answers)
    if verbose:
        print('answers: ', len(answers), sum(list(answers.values())))
    for doc_id in embeds:
        # doc_ids.append(doc_id)
        doc_data = [i * rb.coef_for_embed for i in embeds[doc_id]]
        if add_tf_idf:
            tf_idf_vec = rb.coef_for_tf_idf * tf_idf_features[doc_index[doc_id]]
            tf_idf_list = tf_idf_vec.tolist()
            doc_data.extend(tf_idf_list)
        emb_list.append(doc_data)
        ans_list.append(answers[doc_id])
    return mif_indexes, emb_list, ans_list


def build_rubric_model(tr_data, labels, batch_size):

    vec_size = len(tr_data[0])
    graph = tf.Graph()

    with graph.as_default(), tf.device('/cpu:0'):
        # Input data.
        train_dataset = tf.placeholder(tf.float32, shape=[batch_size, vec_size])
        train_labels = tf.placeholder(tf.float32, shape=[batch_size, 1])

        # Variables.
        weights = tf.Variable(tf.random_uniform([vec_size, 1], -1.0, 1.0))
        # tf.add_to_collection('total_loss', 0.5 * reg_softmax * tf.nn.l2_loss(weights))
        bias = tf.Variable(0.00001)

        y = tf.matmul(train_dataset, weights) + bias

        cross_entropy_array = tf.log(tf.sigmoid(y)) * train_labels + tf.log(1 - tf.sigmoid(y)) * (1 - train_labels)

        cross_entropy = - tf.reduce_mean(cross_entropy_array) + tf.reduce_mean(weights * weights) * reg_coef

        global_step = tf.Variable(0, trainable=False)
        learning_rate = tf.train.exponential_decay(lr, global_step,
                                                   1000, 0.96, staircase=True)
        # Passing global_step to minimize() will increment it at each step.
        train_step = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(cross_entropy, global_step = global_step)
        init = tf.initialize_all_variables()

        sess = tf.Session()
        sess.run(init)

        for i in range(tf_steps):
            sess.run(train_step, feed_dict={train_dataset: tr_data, train_labels: labels})

    model = weights.eval(sess)[:, 0]
    model = model.tolist()
    model.append(float(bias.eval(sess)))
    return model


def test_model(set_id, embedding, rubric_id, tr_set=None, name=''):
    model_id = rb.spot_test_set_embedding_rubric(set_id, embedding, rubric_id, training_set_id=tr_set)
    print('При тестировании для рубрики ', rubric_id, ' использована модель ', model_id)
    # for doc_id in db.get_set_docs(set_id):
    #     rb.spot_doc_rubrics2(doc_id, {rubric_id: None}, verbose=True)
    # model_id = db.get_model(rubric_id)["model_id"]
    # if protocol != '':
    #     file_name = protocol + '_' + name + '.txt'
    result = rb.f1_score(model_id, set_id, rubric_id)
    return result


def teach_and_test(add_tf_idf=False, verbose=False):
    # model_emb_par_teach_or_calc(True)
    # global filename
    # filename = 'ModelEP_0406_128_NonCons_6_3.pic'
    embedding_id = filename
    tr_set = set_list.sets['13']['tr_set_2']
    test_set = set_list.sets['13']['test_set_2']
    rubric_id = set_list.rubrics['3']['pos']
    # в следующей строке до знака равенства написано mif_indexes, emb, ans
    mif_indexes, emb, ans = create_rubric_train_data(tr_set, rubric_id, embedding_id,
                                                     add_tf_idf=add_tf_idf, verbose=verbose)
    batch_size = len(ans)
    answers_array = np.zeros((batch_size, 1))
    answers_array[:, 0] = ans
    if verbose:
        print('start tensorFlow')
    model = build_rubric_model(emb, answers_array, batch_size)
    if verbose:
        print('start put model in bd')
    model_settings = {
        'coef_for_embed': rb.coef_for_embed,
        'coef_for_tf_idf': rb.coef_for_tf_idf
    }
    if add_tf_idf:
        db.put_model(rubric_id, tr_set, model, mif_indexes, len(mif_indexes),
                     embedding=embedding_id, settings=model_settings)
    else:
        db.put_model(rubric_id, tr_set, model, embedding=embedding_id, settings=model_settings)
    print('Результаты рубрикатора на учебной выборке')
    print(test_model(tr_set, embedding_id, rubric_id))
    print('Результаты рубрикатора на тестовой выборке')
    print(test_model(test_set, embedding_id, rubric_id))


def check_reg_paragraph_embedding():
    docs = db.get_set_docs(set_list.sets['pp']['test_set_0'])
    doc_id = str(docs[0])
    vector = np.array(db.get_doc_embedding(embedding_id, doc_id))
    calc_paragraph_embedding2(doc_id)
    vector2 = np.array(db.get_doc_embedding(embedding_id, doc_id))
    print(vector.dot(vector2), vector.dot(vector))


def put_settings_in_model(model_id, coef_for_embed, coef_for_tf_idf):
    session = Driver.db_session()
    model = session.query(RubricationModel).filter(RubricationModel.model_id == model_id).all()[0]
    model.settings = {
        'coef_for_embed': coef_for_embed,
        'coef_for_tf_idf': coef_for_tf_idf
    }
    db.flag_modified(model, "settings")
    session.commit()


def start():
    # start_prepare_docs(True)
    # model_emb_par_teach_or_calc(True)
    # check_reg_paragraph_embedding()
    put_settings_in_model('e9a30a58-bee3-4a36-b94f-02f95c4a2d1d', .1,1)
    # teach_and_test(True)

    # tr_set = set_list.sets['13']['tr_set_2']
    # test_set = set_list.sets['13']['test_set_2']
    # rubric_id = set_list.rubrics['3']['pos']

    # filename = 'ModelEP_1705.pic'
    # mif_indexes, emb, ans = create_rubric_train_data(tr_set, rubric_id, filename, add_tf_idf=True)
    # print(len(emb))
    # print(len(ans))
    # print(emb[0])

    # answers = db.get_rubric_answers(tr_set, rubric_id)
    # mif_indexes, doc_index, res = rb.create_train_data_tf_idf(tr_set, answers)
    # print(type(res), len(res), len(res[0]))
    # print(res[0])


start()


