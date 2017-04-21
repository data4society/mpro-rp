# These are all the modules we'll be using later. Make sure you can import them
# before proceeding further.
# %matplotlib inline
from __future__ import print_function
import collections
import math
import numpy as np
import os
import random
import tensorflow as tf
import zipfile
# from matplotlib import pylab
# from six.moves import range
from six.moves.urllib.request import urlretrieve
# from sklearn.manifold import TSNE


url = 'http://mattmahoney.net/dc/'
consistent_words = True
use_par_embed = True
use_NN = True
learning_rate = 0.3

vocabulary_size = 50000
paragraph_amount = 170000
par_size = 100

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
valid_examples_p = [0,1,2,3,4]
num_sampled = 64  # Number of negative examples to sample.

def maybe_download(filename, expected_bytes):
  """Download a file if not present, and make sure it's the right size."""
  if not os.path.exists(filename):
    filename, _ = urlretrieve(url + filename, filename)
  statinfo = os.stat(filename)
  if statinfo.st_size == expected_bytes:
    print('Found and verified %s' % filename)
  else:
    print(statinfo.st_size)
    raise Exception(
      'Failed to verify ' + filename + '. Can you get to it with a browser?')
  return filename

filename = maybe_download('text8.zip', 31344016)


def read_data(filename):
    """Extract the first file enclosed in a zip file as a list of words"""
    with zipfile.ZipFile(filename) as f:
        data = tf.compat.as_str(f.read(f.namelist()[0])).split()
    return data


words = read_data(filename)
print('Data size %d' % len(words))

assert paragraph_amount * par_size <= len(words)


def build_dataset(words):
    count = [['UNK', -1]]
    count.extend(collections.Counter(words).most_common(vocabulary_size - 1))
    dictionary = dict()
    for word, _ in count:
            dictionary[word] = len(dictionary)
    data = list()
    unk_count = 0
    for word in words:
        if word in dictionary:
            index = dictionary[word]
        else:
            index = 0  # dictionary['UNK']
            unk_count = unk_count + 1
        data.append(index)
    count[0][1] = unk_count
    reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    return data, count, dictionary, reverse_dictionary

data, count, dictionary, reverse_dictionary = build_dataset(words)
print('Most common words (+UNK)', count[:5])
print('Sample data', data[:10])
del words  # Hint to reduce memory.

data_index = 0
par_index = 0


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
    buffer = collections.deque(maxlen=span)
    for _ in range(span):
        buffer.append(data[data_index + par_index * par_size])
        data_index = (data_index + 1) % par_size
        if data_index == 0:
            par_index = (par_index + 1) % paragraph_amount
        # buffer.append(data[data_index])
        # data_index = (data_index + 1) % len(data)
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
        buffer.append(data[data_index + par_index * par_size])
        data_index = (data_index + 1) % par_size
        if data_index == 0:
            par_index = (par_index + 1) % paragraph_amount
        # buffer.append(data[data_index])
        # data_index = (data_index + 1) % len(data)
    return batch, labels


print('data:', [reverse_dictionary[di] for di in data[:8]])

for num_skips, skip_window in [(2, 1), (4, 2)]:
    data_index = 0
    batch, labels = generate_batch(batch_size=8, num_skips=num_skips, skip_window=skip_window)
    print('\nwith num_skips = %d and skip_window = %d:' % (num_skips, skip_window))
    print('    batch:', [reverse_dictionary[bii] if bii < vocabulary_size else bii for bi in batch for bii in bi])
    print('    labels:', [reverse_dictionary[li] for li in labels.reshape(8)])

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

num_steps = 400001

with tf.Session(graph=graph) as session:
    # tf.global_variables_initializer().run()
    session.run(init)
    print('Initialized')
    average_loss = 0
    for step in range(num_steps):
        batch_data, batch_labels = generate_batch(
            batch_size, num_skips, skip_window)
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
        if step % 10000 == 0:
            interesting_pars = {}
            sim = similarity.eval()
            for i in range(valid_size):
                valid_word = reverse_dictionary[valid_examples[i]]
                top_k = 8 # number of nearest neighbors
                nearest = (-sim[i, :]).argsort()[1:top_k+1]
                log = 'Nearest to %s:' % valid_word
                for k in range(top_k):
                    close_word = reverse_dictionary[nearest[k]] if nearest[k] < vocabulary_size else nearest[k] - vocabulary_size
                    log = '%s %s (%s),' % (log, close_word, sim[i, nearest[k]])
                    if nearest[k] >= vocabulary_size:
                        interesting_pars[nearest[k] - vocabulary_size] = ''
                print(log)
    sim_p = similarity_p.eval()
    for i in range(len(valid_examples_p)):
        nearest = (-sim_p[i, :]).argsort()[1:top_k + 1]
        print('Nearest to ')
        print([reverse_dictionary[data[j + i * par_size]] for j in range(par_size)])
        print('IS')
        for k in range(top_k):
            if nearest[k] < vocabulary_size:
                print(reverse_dictionary[nearest[k]])
            else:
                print([reverse_dictionary[data[j + (nearest[k] - vocabulary_size) * par_size]] for j in range(par_size)])

    for par in interesting_pars:
        print(par)
        print([reverse_dictionary[data[i + par * par_size]] for i in range(par_size)])

    final_embeddings = normalized_embeddings.eval()


