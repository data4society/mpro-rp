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
use_NN = False
learning_rate = 0.1

vocabulary_size = 50000
paragraph_amount = 170000
par_size = 100

batch_size = 100
embedding_size = 32 #128  # Dimension of the embedding vector.
embed_par_size = 400
skip_window = 1  # How many words to consider left and right (if not consistent_words)
num_skips = 2  # Size of the window with consistent or random oreder words
l1_size = 32 #256

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
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size, num_skips), dtype=np.int32)
    if not use_NN and use_par_embed:
        labels = np.ndarray(shape=(batch_size), dtype=np.float32)
    else:
        labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    parags = np.ndarray(shape=(batch_size), dtype=np.int32)
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

        if not use_NN and use_par_embed:
            labels[i] = buffer[num_skips]
        else:
            labels[i, 0] = buffer[num_skips]
        parags[i] = par_index
        buffer.append(data[data_index + par_index * par_size])
        data_index = (data_index + 1) % par_size
        if data_index == 0:
            par_index = (par_index + 1) % paragraph_amount
        # buffer.append(data[data_index])
        # data_index = (data_index + 1) % len(data)
    return batch, labels, parags


print('data:', [reverse_dictionary[di] for di in data[:8]])

for num_skips, skip_window in [(2, 1), (4, 2)]:
    data_index = 0
    batch, labels, parags = generate_batch(batch_size=8, num_skips=num_skips, skip_window=skip_window)
    print('\nwith num_skips = %d and skip_window = %d:' % (num_skips, skip_window))
    print('    batch:', [reverse_dictionary[bii] for bi in batch for bii in bi])
    print('    labels:', [reverse_dictionary[li] for li in labels.reshape(8)])
    print('    parags:', parags)


# We pick a random validation set to sample nearest neighbors. here we limit the
# validation samples to the words that have a low numeric ID, which by
# construction are also the most frequent.
valid_size = 16  # Random set of words to evaluate similarity on.
valid_window = 100  # Only pick dev samples in the head of the distribution.
valid_examples = np.array(random.sample(range(valid_window), valid_size))
num_sampled = 64  # Number of negative examples to sample.


graph = tf.Graph()

with graph.as_default(), tf.device('/cpu:0'):
    # Input data.
    train_dataset = tf.placeholder(tf.int32, shape=[batch_size, num_skips])
    train_dataset_p = tf.placeholder(tf.int32, shape=[batch_size])
    if not use_NN and use_par_embed:
        train_labels = tf.placeholder(tf.int32, shape=[batch_size])
    else:
        train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
    valid_dataset = tf.constant(valid_examples, dtype=tf.int32)


    # Variables.
    embeddings = tf.Variable(
        tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
    if use_par_embed:
        embeddings_par = tf.Variable(
            tf.random_uniform([paragraph_amount, embed_par_size], -1.0, 1.0))

    if use_NN:
        weights_l1 = tf.Variable(
            tf.truncated_normal([embedding_size * num_skips, l1_size],
                                stddev=1.0 / math.sqrt(embedding_size)))

        biases_l1 = tf.Variable(tf.zeros([l1_size]))

        if use_par_embed:
            weights_p = tf.Variable(
                tf.truncated_normal([embed_par_size, l1_size],
                                    stddev=1.0 / math.sqrt(embedding_size)))

        softmax_matrix_dim = l1_size
    else:
        if use_par_embed:
            weights_p = tf.Variable(
                tf.truncated_normal([vocabulary_size, embed_par_size ],
                                    stddev=1.0 / math.sqrt(embedding_size)))
        softmax_matrix_dim = embedding_size * num_skips



    softmax_weights = tf.Variable(
        tf.truncated_normal([vocabulary_size, softmax_matrix_dim],
                            stddev=1.0 / math.sqrt(embedding_size)))

    softmax_biases = tf.Variable(tf.zeros([vocabulary_size]))

    # Model.
    # Look up embeddings for inputs.
    embed = tf.nn.embedding_lookup(embeddings, train_dataset)
    embed = tf.reshape(
        embed, [-1, num_skips * embedding_size])
    if use_par_embed:
        embed_p = tf.nn.embedding_lookup(embeddings_par, train_dataset_p)

    # Compute the softmax loss, using a sample of the negative labels each time.
    if use_NN and use_par_embed:
        h = tf.nn.tanh(tf.matmul(embed, weights_l1) + tf.matmul(embed_p, weights_p) + biases_l1)
        loss = tf.reduce_mean(
            tf.nn.sampled_softmax_loss(weights=softmax_weights, biases=softmax_biases, inputs=h,
                                       labels=train_labels, num_sampled=num_sampled, num_classes=vocabulary_size))
    elif use_par_embed:
        # print(embed)
        # print(embed_p)
        # h = tf.concat([1], [embed, embed_p])
        # print(h)
        #
        # print(softmax_weights)
        # print(weights_p)
        # w = tf.concat([1], [softmax_weights, weights_p])
        # print(w)
        #
        # loss = tf.reduce_mean(
        #     tf.nn.sampled_softmax_loss(weights=w, biases=softmax_biases, inputs=h,
        #                                labels=train_labels, num_sampled=num_sampled, num_classes=vocabulary_size))
        loss = tf.reduce_mean(
            tf.nn.sparse_softmax_cross_entropy_with_logits(logits=tf.matmul(embed, tf.transpose(softmax_weights)) +
                                                    tf.matmul(embed_p, tf.transpose(weights_p)) + softmax_biases,
                                                           labels=train_labels))
    elif use_NN:
        h = tf.nn.tanh(tf.matmul(embed, weights_l1) + biases_l1)
        loss = tf.reduce_mean(
            tf.nn.sampled_softmax_loss(weights=softmax_weights, biases=softmax_biases, inputs=h,
                                       labels=train_labels, num_sampled=num_sampled, num_classes=vocabulary_size))
    else:
        loss = tf.reduce_mean(
            tf.nn.sampled_softmax_loss(weights=softmax_weights, biases=softmax_biases, inputs=embed,
                                       labels=train_labels, num_sampled=num_sampled, num_classes=vocabulary_size))

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
    init = tf.initialize_all_variables()

num_steps = 100001

with tf.Session(graph=graph) as session:
  # tf.global_variables_initializer().run()
  session.run(init)
  print('Initialized')
  average_loss = 0
  for step in range(num_steps):
    batch_data, batch_labels, batch_parags = generate_batch(
      batch_size, num_skips, skip_window)
    feed_dict = {train_dataset : batch_data, train_dataset_p : batch_parags, train_labels : batch_labels}
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
      sim = similarity.eval()
      for i in range(valid_size):
        valid_word = reverse_dictionary[valid_examples[i]]
        top_k = 8 # number of nearest neighbors
        nearest = (-sim[i, :]).argsort()[1:top_k+1]
        log = 'Nearest to %s:' % valid_word
        for k in range(top_k):
          close_word = reverse_dictionary[nearest[k]]
          log = '%s %s,' % (log, close_word)
        print(log)
  final_embeddings = normalized_embeddings.eval()
