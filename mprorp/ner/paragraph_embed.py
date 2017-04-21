
import os
import getpass
import sys
import time

import numpy as np
import random
import collections
import tensorflow as tf
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


# set_docs = {}
# for cl in sets:
#     set_docs[cl] = {}
#     for set_type in sets[cl]:
#         set_docs[cl][set_type] = db.get_set_docs(sets[cl][set_type])
#         print(cl, set_type, len(set_docs[cl][set_type]), 'documents')

embedding_for_word_count = 5

consistent_words = True
use_par_embed = False
use_NN = True
learning_rate = 0.3

batch_size = 100
embedding_size = 128 #128  # Dimension of the embedding vector.
# embed_par_size = 400
skip_window = 1  # How many words to consider left and right (if not consistent_words)
num_skips = 3  # Size of the window with consistent or random order words
l1_size = 512 #256

reg_l1 = 0.0001
reg_emded = 0.00005
dropout = 0.7
# reg_softmax = 0.00005

# We pick a random validation set to sample nearest neighbors. here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = 25  # Random set of words to evaluate similarity on.
valid_window = 300  # Only pick dev samples in the head of the distribution.
valid_examples = np.array(random.sample(range(valid_window), valid_size))
num_sampled = 64  # Number of negative examples to sample.

training_set = '1b8f7501-c7a8-41dc-8b06-fda7d04461a2'
train_set_words = db.get_ner_feature(set_id=training_set, feature='embedding')

words_count = {}
set_docs = []
printed = False
print(len(train_set_words))
for doc_id in train_set_words:
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
    if not printed:
        print(doc_words)
        print(doc)
        printed = True

words_count.sort()
print('Most common words (+UNK)', words_count[:5])

dictionary = []
for word in words_count:
    if words_count[word] > embedding_for_word_count:
        dictionary.append(word)

reverse_dictionary = {dictionary[i]: i for i in range(dictionary)}
unk_word = range(dictionary)
no_word = unk_word + 1

paragraphs = []
for doc in set_docs:
    par_words = [no_word for i in range(embedding_for_word_count)]
    for word in doc:
        par_words.append(reverse_dictionary[doc] if doc in reverse_dictionary else unk_word)
    paragraphs.append(par_words)

vocabulary_size = len(reverse_dictionary) + 2
paragraph_amount = len(paragraphs)

data_index = 0
par_index = 0


def new_buffer(span):
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
    return buffer


def generate_batch(batch_size, num_skips, skip_window):
    global data_index
    global par_index
    global use_par_embed

    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window

    batch = np.ndarray(shape=(batch_size, num_skips + use_par_embed), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    if consistent_words:
        span = num_skips + 1  # [ skip_window target skip_window ]
    else:
        span = 2 * skip_window + 1 # [ skip_window target skip_window ]
    buffer = new_buffer(span)

    for i in range(batch_size):
        if not consistent_words:
            target = skip_window  # target label at the end of the buffer
            targets_to_avoid = [ skip_window ]
        for j in range(num_skips):
            if not consistent_words:
                while target in targets_to_avoid:
                    target = random.randint(0, span - 1)
                targets_to_avoid.append(target)
                batch[i, j] = buffer[target]
            else:
                batch[i, j] = buffer[j]
        if use_par_embed:
            batch[i, num_skips] = par_index + vocabulary_size

        labels[i, 0] = buffer[num_skips]
        buffer.append(buffer.append(paragraphs[par_index][data_index]))
        data_index += 1
        if data_index == len(paragraphs[par_index]):
            par_index = (par_index + 1) % len(paragraphs)
            data_index = 0
            buffer = new_buffer(span)
        # buffer.append(data[data_index])
        # data_index = (data_index + 1) % len(data)
    return batch, labels

