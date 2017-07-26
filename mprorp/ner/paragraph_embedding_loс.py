
import sys

import numpy as np
import random
import collections
import tensorflow as tf
import math
import mprorp.analyzer.db as db
import pickle as pickle
from mprorp.utils import home_dir
import mprorp.ner.set_list as set_list

import json

data_filename = 'data.json'

embedding_for_word_count = 5
learning_steps = 30000
calc_steps = 300

verbose = True

params_consistent_words = True
use_par_embed = True
use_NN = True
learning_rate = 1

params_batch_size = 100
params_embedding_size = 128  # 128  # Dimension of the embedding vector.
# embed_par_size = 400
params_skip_window =  1  # How many words to consider left and right (if not consistent_words)
params_num_skips = 3  # Size of the window with consistent or random order words
params_l1_size =  512  # 256

reg_l1 = 0.0001
reg_emded = 0.00005
dropout = 0.7

filename = 'ModelEP_0406_128_NonCons_6_3.pic'

# parameters for rubrication
reg_coef =  0.000005
lr= 0.0025
tf_steps = 100000

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


#
def words_to_file(doc_list, filename=None, type=0):
    if filename is None:
        filename = data_filename
    set_to_file = {}
    printed = False
    if type<2:
        train_set_words = db.get_ner_feature(doc_id_list=doc_list, feature='embedding')
        print('end reading from db')

        count = 0
        for doc_id in train_set_words:
            count += 1
            if count % 1000 == 0:
                print(count)
            doc_words = train_set_words[doc_id]
            doc = []
            for element in doc_words:
                if type == 0:
                    main_word = ''
                    rate = 0
                    if not printed:
                        print(element)
                        printed = True
                    for word in element[2]:
                        if rate < element[2][word]:
                            rate = element[2][word]
                            main_word = word
                    doc.append(main_word)
                else:
                    doc.append(element[2])
            set_to_file[doc_id] = doc
    else:
        for doc_id in doc_list:
            if type==2:
                set_to_file[doc_id] = db.get_morpho(doc_id)
            else:
                set_to_file[doc_id] = db.get_doc_text(doc_id)
            if not printed:
                print(set_to_file[doc_id])
                printed = True
    print('start dump')
    with open(home_dir + '/' + filename, 'w') as f:
        json.dump(set_to_file, f)
#

def append_doc_words(train_set_words, doc_list, set_docs, new_dictionary, words_count, doc_ids):

    for doc_id in doc_list:
        if doc_id in doc_ids:
            print('skip doc ', doc_id, ' длина doc_ids ', len(doc_ids))
            continue
        # if verbose and len(set_docs) % 1000 == 0:
        #     print('set_docs: ', len(set_docs))
        doc = train_set_words[doc_id]
        # doc = []
        for main_word in doc:

            if new_dictionary:
                if main_word in words_count:
                    words_count[main_word] += 1
                else:
                    words_count[main_word] = 1
        set_docs.append(doc)
        doc_ids.append(doc_id)


def fill_paragraphs_for_learning(num_skips, doc_id=None, dictionary=None, reverse_dictionary=None, verbose=False):

    with open(home_dir + '/' + data_filename, 'r') as f:
    # with open(data_filename, 'r') as f:
        training_set = json.load(f)

    new_dictionary = dictionary is None

    paragraphs = []
    words_count = {}
    set_docs = []
    doc_ids=[]

    if doc_id is None:
        train_set_docs = [str(i) for i in training_set.keys()]
    else:
        train_set_docs = [doc_id]
    start_doc = 0
    while len(train_set_docs) - start_doc > 2000:
        append_doc_words(training_set, train_set_docs[start_doc: start_doc + 1250], set_docs, new_dictionary, words_count, doc_ids)
        start_doc += 1250
    append_doc_words(training_set, train_set_docs[start_doc:], set_docs, new_dictionary, words_count, doc_ids)

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
        par_words = [no_word for i in range(num_skips)] # В начало параграфа добавим полное окно путсых слов
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

    assert use_par_embed or learning  # If we use existed model (learning=False), use_par_embed must be True

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

    with graph.as_default():
    # with graph.as_default(), tf.device('/gpu:0'):
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
            embeddings = tf.concat([embeddings_w, embeddings_p], 0)
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

        # tf.summary.scalar('cross_entropy', cross_entropy)
        tf.add_to_collection('total_loss', cross_entropy)
        loss = tf.add_n(tf.get_collection('total_loss'))
        # tf.summary.scalar('loss', loss)

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
        # merged = tf.summary.merge_all()
        # train_writer = tf.summary.FileWriter(home_dir + '/train_summary')
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
            _, l, cross_e = session.run([optimizer, loss, cross_entropy], feed_dict=feed_dict)
            # summary, _, l = session.run([merged, optimizer, loss], feed_dict=feed_dict)
            # train_writer.add_summary(summary, step)
            average_loss += l
            if verbose and step % 10 == 0:
                sys.stdout.write('\r{} / {} : loss = {}'.format(
                    step, num_steps, average_loss/step))
                sys.stdout.flush()
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
            with open(filename, 'wb') as f:
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
            # for i in range(len(valid_examples_p)):
            #     nearest = (-sim_p[i, :]).argsort()[1:top_k + 1]
            #     print('Nearest to ')
            #     if doc_txt.get(doc_ids[i], None) is None:
            #         doc_txt[doc_ids[i]] = db.get_doc_text(doc_ids[i])
            #     print(doc_txt[doc_ids[i]])
            #     print('---------------------------------===================================--------------------------------------')
            #     # print([dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])
            #     print('IS')
            #     for k in range(top_k):
            #         if nearest[k] < vocabulary_size:
            #             print(sim_p[i,nearest[k]], dictionary[nearest[k]])
            #             print('---------------------------------===================================--------------------------------------')
            #         else:
            #             doc_id = doc_ids[nearest[k] - vocabulary_size]
            #             if doc_txt.get(doc_id, None) is None:
            #                 doc_txt[doc_id] = db.get_doc_text(doc_id)
            #             print(sim_p[i,nearest[k]], doc_txt[doc_id])
            #             print('---------------------------------===================================--------------------------------------')
            #             # print(sim_p[i,nearest[k]], [dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])
            # if verbose:
            #     for par in interesting_pars:
            #         print(par)
            #         if doc_txt.get(doc_ids[par], None) is None:
            #             doc_txt[doc_ids[par]] = db.get_doc_text(doc_ids[par])
            #         print(doc_txt[doc_ids[par]])
            #         print('---------------------------------===================================--------------------------------------')
                    # print([dictionary[paragraphs[i][j]] for j in range(len(paragraphs[i]))])

        if learning:
            return None
        else:
            return embeddings_p.eval()


def model_emb_par_teach_or_calc(teach=True):


    if teach:
        paragraphs, doc_ids, word_list, reverse_dictionary = fill_paragraphs_for_learning(params_num_skips, verbose=verbose)
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

        with open(filename, 'rb') as f:
            model_params = pickle.load(f)

        if verbose:
            print('fill paragraphs start')
        paragraphs, doc_ids, _, _ = fill_paragraphs_for_learning(model_params['params']['num_skips'],
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
        if verbose:
            print('docs embedding is ready')


def words_to_files(set_type):
    set_id = set_list.sets['pp'][set_type + '_set_2']
    doc_list_0 = []
    doc_list_1 = []
    rubric_id = set_list.rubrics['pp']['pos']
    answers = db.get_rubric_answers(set_id, rubric_id)
    print(len(answers))
    for doc_id in answers:
        if answers[doc_id]:
            doc_list_1.append(doc_id)
        else:
            doc_list_0.append(doc_id)

    print(len(doc_list_0))
    print(len(doc_list_1))
    for type in range(4):
        words_to_file(doc_list_0, 'data_' + set_type + '_False_' + str(type) + '.json', type)
        print(set_type, type, False)
        words_to_file(doc_list_0, 'data_' + set_type + '_True_' + str(type) + '.json', type)
        print(set_type, type, True)
    print('ok')

# model_emb_par_teach_or_calc(True)