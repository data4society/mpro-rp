"""functions for training NER model"""

import os
import getpass
import sys
import time

import numpy as np
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

sets = dict()
# sets['oc_class_person'] = {'train': '2e366853-4533-4bd5-a66e-92a834a1a2ca',
#                            'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}
# sets['name'] = {'train': '4fb42fd1-a0cf-4f39-9206-029255115d01', # Исходная выборка 274 + 77
#                 'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'}

sets['name'] = {'train': set_list.sets1250[29],
                'dev': set_list.sets100[0]}
                # 'dev': set_list.sets1250[29]}
                # 'dev': 'f861ee9d-5973-460d-8f50-92fca9910345'} # Исходная dev-выборка 77
sets['loc'] = {'train': set_list.sets1250[0],
                'dev': set_list.sets1250[29]}
# {'train': set_list.sets100[0],
#                'dev': set_list.sets100[1]}


# sets['oc_class_org'] = {'train': '78f8c9fb-e385-442e-93b4-aa1a18e952d0',
#                         'dev': '299c8bd1-4e39-431d-afa9-398b2fb23f69'}
# sets['oc_class_loc'] = {'train': '74210e3e-0127-4b21-b4b7-0b55855ca02e',
#                         'dev': '352df6b5-7659-4f8c-a68d-364400a5f0da'}


class Config(object):
    """Holds model hyperparams and data information.

    The config class is used to store various hyperparameters and dataset
    information parameters. Model objects are passed a Config() object at
    instantiation.
    """
    windows_in_epoch = True
    windows_in_epoch_dev = False
    classes = ['oc_class_person', 'name', 'oc_class_org', 'oc_class_loc', 'loc']
    tag_types = [['B', 'I', 'S', 'E'], ['BS', 'IE'], ['BI', 'ES']]
    special_tag_types = {'oc_class_person':
                             [['oc_span_last_name', 'oc_span_first_name', 'oc_span_middle_name',
                               'oc_span_nickname', 'oc_span_foreign_name'],
                              ['oc_span_post', 'oc_span_role', 'oc_span_status']]}
    learn_type = {'class': 4, 'tags': 1}

    new_model = True

    embed_size = 1000
    hidden_size = 500 # 500
    l2_embed = 0.001
    l2_2lay = 0.00325
    window_size = 7 # 11
    pre_embedding = True
    train_embedding = False

    # embed_size = 50
    # hidden_size = 100
    # l2_embed = 0.001
    # l2_2lay =  0.00325
    # window_size = 7 # 11
    # pre_embedding = False
    # train_embedding = True

    batch_size = 256 # 128
    label_size = 5
    max_epochs = 24
    early_stopping = 6
    dropout1 = 0.5
    dropout2 = 0.6
    lr = 0.001
    l2_feat = 0.00015
    training_set = u'4fb42fd1-a0cf-4f39-9206-029255115d01'
    dev_set = u'f861ee9d-5973-460d-8f50-92fca9910345'

    embedding_for_word_count = 6
    # pre_embedding_from_file = home_dir + '/embeddings/news_win20.model.bin'
    pre_embedding_from_file = ''
    # embedding = 'first_test_embedding'
    embedding = 'second_embedding_1000'
    word_unkn = 'etiraz_UNKN'

    feature_answer = ['person_answer']
    # feature_answer = 'org_answer'
    # features = []
    # features = ['Org']
    # features = ['Org', 'Person', 'Loc', 'Date', 'Prof', 'morpho', 'Capital']

    features = ['morpho', 'Capital', 'Prof', 'Loc']
    # features = ['morpho', 'Capital']
    # features = ['morpho', 'Person']
    print(features)
    features_length = 0
    for feat in features:
        features_length += features_size[feat]
    feature_type = 0

def xavier_weight_init():

  def _xavier_initializer(shape, **kwargs):
    """Defines an initializer for the Xavier distribution.

    This function will be used as a variable scope initializer.

    https://www.tensorflow.org/versions/r0.7/how_tos/variable_scope/index.html#initializers-in-variable-scope

    Args:
      shape: Tuple or 1-d array that species dimensions of requested tensor.
    Returns:
      out: tf.Tensor of specified shape sampled from Xavier distribution.
    """

    m = shape[0]
    n = shape[1] if len(shape) > 1 else shape[0]

    bound = np.sqrt(6) / np.sqrt(m + n)
    out = tf.random_uniform(shape, minval=-bound, maxval=bound)

    return out

  return _xavier_initializer


class NERModel(LanguageModel):
    """Implements a NER (Named Entity Recognition) model.

    This class implements a deep network for named entity recognition. It
    inherits from LanguageModel, which has an add_embedding method in addition to
    the standard Model method.
    """

    def load_data_db(self, debug=False, verbose=False):
        """Loads starter word-vectors and train/dev/test data."""
        # Load the starter word vectors
        training_set = self.config.training_set
        #  train_set_words[doc_id] = [(sentence, word, [lemma1, lemma2]), ... (...)]
        if verbose:
            print('start reading training words', time.clock())
        train_set_words = db.get_ner_feature(set_id=training_set, feature='embedding')
        if verbose:
            print('reading training words - ok', time.clock())
            print('start reading dev words', time.clock())

        dev_set = self.config.dev_set
        #  dev_set_words[doc_id] = [(sentence, word, [lemma1, lemma2]), ... (...)]
        dev_set_words = db.get_ner_feature(set_id=dev_set, feature='embedding')
        if verbose:
            print('reading dev words - ok', time.clock())

        # collect words from set

        words_for_embedding = {}
        if Config.pre_embedding:
            for set_words in [train_set_words, dev_set_words]:
                for doc_id in set_words:
                    doc_words = set_words[doc_id]
                    for element in doc_words:
                        for word in element[2]:
                            words_for_embedding[word] = ''
            words_for_embedding[self.config.word_unkn] = ''
            if verbose:
                print(len(words_for_embedding))

            if self.config.pre_embedding_from_file == '':
                if verbose:
                    print('start reading training embeddings', time.clock())
                wv_dict = db.get_multi_word_embedding(self.config.embedding, words_for_embedding.keys())
                if verbose:
                    print('reading training embeddings - ок', time.clock())
                    print('wv_dict_len', len(list(wv_dict.keys())))
            else:
                # model_w2v = word2vec.Word2Vec.load_word2vec_format(self.config.pre_embedding_from_file, binary=True)
                # wv_dict = {}
                # for word in words_for_embedding:
                #     if word in model_w2v.vocab:
                #         wv_dict[word] = model_w2v[word]
                # model_w2v = None
                raise 'we do not use loading embedding from file'
        else:
            words_count = {}
            for doc_id in train_set_words:
                doc_words = train_set_words[doc_id]
                for element in doc_words:
                    for word in element[2]:
                        if word in words_count:
                            words_count[word] += 1
                        else:
                            words_count[word] = 1

            wv_dict = {}
            for word in words_count:
                if words_count[word] > Config.embedding_for_word_count:
                    wv_dict[word] = ''


        # Create word_to_num and LookUp table (wv)

        # If word not in wv_dict (in embedding) we change it with 'UUUNKKK' = 0
        # We can append random array for such word
        if not self.config.pre_embedding:
            wv_array = [np.random.uniform(-0.1, 0.1, Config.embed_size)]
        elif self.config.word_unkn in wv_dict:
            wv_array = [wv_dict[self.config.word_unkn]]
        else:
            # pre_embedding, но нет вектора для редкого слова
            wv_array = [np.random.uniform(-0.1, 0.1, Config.embed_size)]

        word_to_num = {'UUUNKKK': 0}
        count = 1
        for word in wv_dict:
            word_to_num[word] = count
            if Config.pre_embedding:
                wv_array.append(wv_dict[word])
            else:
                wv_array.append(np.random.uniform(-0.1, 0.1, Config.embed_size))
            count += 1

        # if verbose:
            # print(word_to_num)

        self.wv = np.array(wv_array, dtype=np.float32)
        # model_w2v = None

        if verbose:
            print(self.config.feature_answer)
            print(self.config.feature_type)
            print('start reading training answers', time.clock())
        answers = db.get_ner_feature_dict(set_id=training_set, feature_type=self.config.feature_type,
                                          feature_list=self.config.feature_answer)
        if verbose:
            print('reading training answers - ок', time.clock())

        tagnames = [0]
        for doc_id in answers:
            for key in answers[doc_id]:
                ans = answers[doc_id][key]
                # ans_tuple = (ans[0], ans[1])
                ans_tuple = ans
                if not (ans_tuple in tagnames):
                    tagnames.append(ans_tuple)

        print(tagnames)
        if verbose and self.config.train_embedding:
            x = open('NER_' + str(training_set) + '_' + str(tagnames[1]) + '.py', 'a', encoding='utf-8')
            x.write('word_to_num = ' + str(word_to_num) + '\n')
            x.write('words_for_embedding = ' + str(words_for_embedding) + '\n')
            x.close()
            saver(word_to_num, words_for_embedding, training_set, str(tagnames[1]))
            print('saving done')

        self.config.label_size = len(tagnames)
        self.num_to_tag = dict(enumerate(tagnames))
        tag_to_num = {v: k for k, v in iter(self.num_to_tag.items())}

        features_set = {}
        for feat in self.config.features:
            if verbose:
                print('start reading training feature', feat, time.clock())
            features_set[feat] = db.get_ner_feature_dict(set_id=training_set, feature=feat)
            if verbose:
                print('reading training feature', feat, '- ok', time.clock())

        self.train_data = {'words': train_set_words, 'answers': answers, 'features': features_set}
        self.word_to_num, self.tag_to_num = word_to_num, tag_to_num
        if not self.config.windows_in_epoch:
            self.feat_train, self.X_train, self.y_train, _, _ = du.docs_to_windows2(self.train_data, word_to_num,
                                                        tag_to_num, self.config.features,
                                                        features_size, self.config.features_length,
                                                        wsize=self.config.window_size)
        else:
            self.feat_train, self.X_train, self.y_train = [], [], []

        # dev_set
        answers = db.get_ner_feature_dict(set_id=dev_set, feature_type=self.config.feature_type,
                                          feature_list=self.config.feature_answer)
        features_set = {}
        for feat in self.config.features:
            features_set[feat] = db.get_ner_feature_dict(set_id=dev_set, feature=feat)
        self.dev_data = {'words': dev_set_words, 'answers': answers, 'features': features_set}
        if not self.config.windows_in_epoch_dev:
            self.feat_dev, self.X_dev, self.y_dev, self.w_dev, _ = du.docs_to_windows2(self.dev_data, word_to_num,
                                                         tag_to_num, self.config.features,
                                                         features_size, self.config.features_length,
                                                         wsize=self.config.window_size)
        else:
            self.feat_dev, self.X_dev, self.y_dev, self.w_dev = [], [], [], []

        self.word_to_num = word_to_num
        self.tag_to_num = tag_to_num
        print("Размер учебной выборки: ", len(self.X_train))

        # self.tagnames = tagnames

    def load_data_file(self, doc_id, session, debug=False):
        """Loads starter word-vectors and train/dev/test data."""
        # Load the starter word vectors
        # training_set = self.config.training_set
        #  train_set_words[doc_id] = [(sentence, word, [lemma1, lemma2]), ... (...)]
        # doc_set_words = {}
        # doc_set_words[doc_id] = db.get_ner_feature_one_feature(doc_id=doc_id, feature='embedding', session=session)
        doc_set_words = db.get_ner_feature(doc_id=doc_id, feature='embedding', session=session)

        if Config.pre_embedding:
            words_for_embedding = {}
            for doc_id in doc_set_words:
                doc_words = doc_set_words[doc_id]
                for element in doc_words:
                    for word in element[2]:
                        words_for_embedding[word] = ''
            words_for_embedding[self.config.word_unkn] = ''
            # if verbose:
            #     print(words_for_embedding)

            if self.config.pre_embedding_from_file == '':
                wv_dict = db.get_multi_word_embedding(self.config.embedding, words_for_embedding.keys())
            else:
                # model_w2v = word2vec.Word2Vec.load_word2vec_format(self.config.pre_embedding_from_file, binary=True)
                # wv_dict = {}
                # for word in words_for_embedding:
                #     if word in model_w2v.vocab:
                #         wv_dict[word] = model_w2v[word]
                # print('found words', len(wv_dict), wv_dict.keys())
                # model_w2v = None
                raise 'we do not use loading embedding from file'
            if self.config.word_unkn in wv_dict:
                wv_array = [wv_dict[self.config.word_unkn]]
            else:
                # pre_embedding, но нет вектора для редкого слова
                wv_array = [np.random.uniform(-0.1, 0.1, Config.embed_size)]

            word_to_num = {'UUUNKKK': 0}
            count = 1
            for word in wv_dict:
                word_to_num[word] = count
                wv_array.append(wv_dict[word])
                count += 1
            self.wv = np.array(wv_array, dtype=np.float32)
            self.word_to_num = word_to_num

        # -------------------------------------------------
        self.config.label_size = len(self.tag_to_num)

        features_set = {}
        for feat in self.config.features:
            features_set[feat] = db.get_ner_feature_dict(doc_id=doc_id, feature=feat, session=session)

        doc_data = {'words': doc_set_words, 'answers': {}, 'features': features_set}
        self.feat_test, self.X_test, self.y_test, _, self.indexes = du.docs_to_windows2(doc_data, self.word_to_num,
                                                                             self.tag_to_num,
                                                                             self.config.features,
                                                                             features_size,
                                                                             self.config.features_length,
                                                                             wsize=self.config.window_size)


        # self.tagnames = tagnames


    def load_data(self, debug=False):
        """Loads starter word-vectors and train/dev/test data."""
        # Load the starter word vectors
        self.wv, word_to_num, num_to_word = ner.load_wv(
            'data/ner/vocab.txt', 'data/ner/wordVectors.txt')
        tagnames = ['O', 'LOC', 'MISC', 'ORG', 'PER']
        self.num_to_tag = dict(enumerate(tagnames))
        tag_to_num = {v: k for k, v in iter(self.num_to_tag.items())}

        # Load the training set
        docs = du.load_dataset('data/ner/train')
        self.X_train, self.y_train = du.docs_to_windows(
            docs, word_to_num, tag_to_num, wsize=self.config.window_size)
        if debug:
            self.X_train = self.X_train[:1024]
            self.y_train = self.y_train[:1024]

        # Load the dev set (for tuning hyperparameters)
        docs = du.load_dataset('data/ner/dev')
        self.X_dev, self.y_dev = du.docs_to_windows(
            docs, word_to_num, tag_to_num, wsize=self.config.window_size)
        if debug:
            self.X_dev = self.X_dev[:1024]
            self.y_dev = self.y_dev[:1024]

        # Load the test set (dummy labels only)
        docs = du.load_dataset('data/ner/test.masked')
        self.X_test, self.y_test = du.docs_to_windows(
            docs, word_to_num, tag_to_num, wsize=self.config.window_size)


    def add_placeholders(self):
        """Generate placeholder variables to represent the input tensors

      These placeholders are used as inputs by the rest of the model building
      code and will be fed data during training.  Note that when "None" is in a
      placeholder's shape, it's flexible

      Adds following nodes to the computational graph

      input_placeholder: Input placeholder tensor of shape
                         (None, window_size), type tf.int32
      labels_placeholder: Labels placeholder tensor of shape
                          (None, label_size), type tf.float32
      dropout_placeholder: Dropout value placeholder (scalar),
                           type tf.float32

      Add these placeholders to self as the instance variables
  
          self.input_placeholder
          self.labels_placeholder
          self.dropout_placeholder

    (Don't change the variable names)
    """
        ### YOUR CODE HERE
        self.input_placeholder = tf.placeholder(
            tf.int32, shape=[None, self.config.window_size], name='Input')

        self.features_placeholder = tf.placeholder(
            tf.float32, shape=[None, self.config.window_size * self.config.features_length], name='Feat_Input')

        self.labels_placeholder = tf.placeholder(
            tf.float32, shape=[None, self.config.label_size], name='Target')
        self.dropout1_placeholder = tf.placeholder(tf.float32, name='Dropout1')
        self.dropout2_placeholder = tf.placeholder(tf.float32, name='Dropout2')
        ### END YOUR CODE

    def create_feed_dict(self, input_batch, dropout1, dropout2, label_batch=None, feat_batch=None):
        """Creates the feed_dict for softmax classifier.

        A feed_dict takes the form of:

        feed_dict = {
            <placeholder>: <tensor of values to be passed for placeholder>,
            ....
        }


        Hint: The keys for the feed_dict should be a subset of the placeholder
              tensors created in add_placeholders.
        Hint: When label_batch is None, don't add a labels entry to the feed_dict.

        Args:
          input_batch: A batch of input data.
          label_batch: A batch of label data.
        Returns:
          feed_dict: The feed dictionary mapping from placeholders to values.
        """
        ### YOUR CODE HERE
        feed_dict = {
            self.input_placeholder: input_batch,
        }
        if label_batch is not None:
            feed_dict[self.labels_placeholder] = label_batch
        if dropout1 is not None:
            feed_dict[self.dropout1_placeholder] = dropout1
        if dropout2 is not None:
            feed_dict[self.dropout2_placeholder] = dropout2
        if feat_batch is not None:
            feed_dict[self.features_placeholder] = feat_batch
        elif self.config.features_length > 0:
            feed_dict[self.features_placeholder] = np.zeros(self.config.window_size * self.config.features_length)

        ### END YOUR CODE
        return feed_dict


    def add_embedding(self, pre_embedding):
        """Add embedding layer that maps from vocabulary to vectors.

        Creates an embedding tensor (of shape (len(self.wv), embed_size). Use the
        input_placeholder to retrieve the embeddings for words in the current batch.

        (Words are discrete entities. They need to be transformed into vectors for use
        in deep-learning. Although we won't do so in this problem, in practice it's
        useful to initialize the embedding with pre-trained word-vectors. For this
        problem, using the default initializer is sufficient.)

        Hint: This layer should use the input_placeholder to index into the
              embedding.
        Hint: You might find tf.nn.embedding_lookup useful.
        Hint: See following link to understand what -1 in a shape means.
          https://www.tensorflow.org/versions/r0.8/api_docs/python/array_ops.html#reshape
        Hint: Check the last slide from the TensorFlow lecture.
        Hint: Here are the dimensions of the variables you will need to create:

            L: (len(self.wv), embed_size)

        Returns:
            window: tf.Tensor of shape (-1, window_size*embed_size)
        """
        # The embedding lookup is currently only implemented for the CPU
        with tf.device('/cpu:0'):
            ### YOUR CODE HERE
            if pre_embedding:
                embedding = tf.Variable(self.wv, name='Embedding', trainable=self.config.train_embedding)
            else:
                embedding = tf.get_variable('Embedding', [len(self.word_to_num), self.config.embed_size])
            # embedding = tf.Variable(self.wv, name='Embedding')
            window = tf.nn.embedding_lookup(embedding, self.input_placeholder)
            window = tf.reshape(
                window, [-1, self.config.window_size * self.config.embed_size])
          ### END YOUR CODE
            return window

    def add_model(self, window):
        """Adds the 1-hidden-layer NN.

        Hint: Use a variable_scope (e.g. "Layer") for the first hidden layer, and
              another variable_scope (e.g. "Softmax") for the linear transformation
              preceding the softmax. Make sure to use the xavier_weight_init you
              defined in the previous part to initialize weights.
        Hint: Make sure to add in regularization and dropout to this network.
              Regularization should be an addition to the cost function, while
              dropout should be added after both variable scopes.
        Hint: You might consider using a tensorflow Graph Collection (e.g
              "total_loss") to collect the regularization and loss terms (which you
              will add in add_loss_op below).
        Hint: Here are the dimensions of the various variables you will need to
              create

              W:  (window_size*embed_size, hidden_size)
              b1: (hidden_size,)
              U:  (hidden_size, label_size)
              b2: (label_size)

        https://www.tensorflow.org/versions/r0.7/api_docs/python/framework.html#graph-collections
        Args:
            window: tf.Tensor of shape (-1, window_size*embed_size)
        Returns:
            output: tf.Tensor of shape (batch_size, label_size)
        """
        ### YOUR CODE HERE
        with tf.variable_scope('Layer1', initializer=xavier_weight_init()) as scope:
            W = tf.get_variable(
                'W', [self.config.window_size * self.config.embed_size,
                    self.config.hidden_size])
            b1 = tf.get_variable('b1', [self.config.hidden_size])
            if self.config.features_length > 0:
                Wf = tf.get_variable(
                    'Wf', [self.config.window_size * self.config.features_length,
                           self.config.hidden_size])
                h = tf.nn.tanh(tf.matmul(window, W) + tf.matmul(self.features_placeholder, Wf) + b1)
            else:
                h = tf.nn.tanh(tf.matmul(window, W) + b1)
            h_drop = tf.nn.dropout(h, self.dropout1_placeholder)
            if self.config.l2_embed:
                tf.add_to_collection('total_loss', 0.5 * self.config.l2_embed * tf.nn.l2_loss(W))
                if self.config.features_length > 0:
                    tf.add_to_collection('total_loss', 0.5 * self.config.l2_feat * tf.nn.l2_loss(Wf))



        with tf.variable_scope('Layer2', initializer=xavier_weight_init()) as scope:
            U = tf.get_variable('U', [self.config.hidden_size, self.config.label_size])
            b2 = tf.get_variable('b2', [self.config.label_size])
            y = tf.matmul(h_drop, U) + b2
            if self.config.l2_2lay:
                tf.add_to_collection('total_loss', 0.5 * self.config.l2_2lay * tf.nn.l2_loss(U))
        output = tf.nn.dropout(y, self.dropout2_placeholder)
        ### END YOUR CODE
        return output

    def add_loss_op(self, y):
        """Adds cross_entropy_loss ops to the computational graph.

        Hint: You can use tf.nn.softmax_cross_entropy_with_logits to simplify your
              implementation. You might find tf.reduce_mean useful.
        Args:
          pred: A tensor of shape (batch_size, n_classes)
        Returns:
          loss: A 0-d tensor (scalar)
        """
        ### YOUR CODE HERE
        cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(y, self.labels_placeholder))
        tf.add_to_collection('total_loss', cross_entropy)
        loss = tf.add_n(tf.get_collection('total_loss'))
        ### END YOUR CODE
        return loss

    def add_training_op(self, loss):
        """Sets up the training Ops.

        Creates an optimizer and applies the gradients to all trainable variables.
        The Op returned by this function is what must be passed to the
        `sess.run()` call to cause the model to train. See

        https://www.tensorflow.org/versions/r0.7/api_docs/python/train.html#Optimizer

        for more information.

        Hint: Use tf.train.AdamOptimizer for this model.
              Calling optimizer.minimize() will return a train_op object.

        Args:
          loss: Loss tensor, from cross_entropy_loss.
        Returns:
          train_op: The Op for training.
        """
        ### YOUR CODE HERE
        optimizer = tf.train.AdamOptimizer(self.config.lr)
        global_step = tf.Variable(0, name='global_step', trainable=False)
        train_op = optimizer.minimize(loss, global_step=global_step)
        ### END YOUR CODE
        return train_op

    def __init__(self, params, session=None):
        """Constructs the network using the helper functions defined above."""
        self.config = params['config']
        # self.load_data(debug=False)
        if self.config.new_model:
            self.load_data_db(debug=False, verbose=True)
            # print('train_data words type after', type(self.train_data['words']))
        else:
            self.word_to_num = params['words']
            self.tag_to_num = params['tags']
            self.load_data_file(self.config.doc.doc_id, session, debug=False)

        self.add_placeholders()
        # window = self.add_embedding(self.config.pre_embedding if self.config.new_model else False)
        window = self.add_embedding(self.config.pre_embedding)
        y = self.add_model(window)

        self.loss = self.add_loss_op(y)
        self.predictions = tf.nn.softmax(y)
        one_hot_prediction = tf.argmax(self.predictions, 1)
        correct_prediction = tf.equal(
            tf.argmax(self.labels_placeholder, 1), one_hot_prediction)
        self.correct_predictions = tf.reduce_sum(tf.cast(correct_prediction, 'int32'))
        self.train_op = self.add_training_op(self.loss)
        # self.train_data = {'words': None, 'answers': None, 'features': None}
        # self.dev_data   = {'words': None, 'answers': None, 'features': None}

    def run_epoch(self, session, input_data, input_labels, input_features, shuffle=True, verbose=True):
        orig_features, orig_X, orig_y = input_features, input_data, input_labels
        dp1 = self.config.dropout1
        dp2 = self.config.dropout2
        # We're interested in keeping track of the loss and accuracy during training
        total_loss = []
        total_correct_examples = 0
        total_processed_examples = 0
        total_steps = len(orig_X) / self.config.batch_size
        if self.config.windows_in_epoch:
            for step, (x, y, f) in enumerate(
                data_iterator2(self.train_data, self.word_to_num, self.tag_to_num,
                               self.config.features, features_size,  self.config.features_length,
                               self.config.window_size,
                               batch_size=self.config.batch_size,
                           label_size=self.config.label_size, shuffle=shuffle)):
                feed = self.create_feed_dict(input_batch=x, dropout1=dp1, dropout2=dp2, label_batch=y, feat_batch=f)
                loss, total_correct, _ = session.run(
                    [self.loss, self.correct_predictions, self.train_op],
                    feed_dict=feed)
                total_processed_examples += len(x)
                total_correct_examples += total_correct
                total_loss.append(loss)
                ##
                if verbose and step % verbose == 0:
                    sys.stdout.write('\r{} / {} : loss = {}'.format(
                        step, total_steps, np.mean(total_loss)))
                    sys.stdout.flush()

            print('123')
        else:
            for step, (x, y, f) in enumerate(
                data_iterator(orig_X, orig_y, orig_features, batch_size=self.config.batch_size,
                           label_size=self.config.label_size, shuffle=shuffle)):
                feed = self.create_feed_dict(input_batch=x, dropout1=dp1, dropout2=dp2, label_batch=y, feat_batch=f)
                loss, total_correct, _ = session.run(
                    [self.loss, self.correct_predictions, self.train_op],
                    feed_dict=feed)
                total_processed_examples += len(x)
                total_correct_examples += total_correct
                total_loss.append(loss)
                ##
                if verbose and step % verbose == 0:
                    sys.stdout.write('\r{} / {} : loss = {}'.format(
                        step, total_steps, np.mean(total_loss)))
                    sys.stdout.flush()
        if verbose:
            sys.stdout.write('\r')
            sys.stdout.flush()
        return np.mean(total_loss), total_correct_examples / float(total_processed_examples)

    def predict(self, session, X, y=None, features=None):
        """Make predictions from the provided model."""
        # If y is given, the loss is also calculated
        # We deactivate dropout by setting it to 1
        dp = 1
        losses = []
        results = []
        data = data_iterator(X, y, features, batch_size=self.config.batch_size,
                             label_size=self.config.label_size, shuffle=False)

        # if np.any(y):
        #     data = data_iterator(X, y, features, batch_size=self.config.batch_size,
        #                          label_size=self.config.label_size, shuffle=False)
        # else:
        #     data = data_iterator(X, batch_size=self.config.batch_size,
        #                          label_size=self.config.label_size, shuffle=False)
        for step, (x, y, f) in enumerate(data):
            feed = self.create_feed_dict(input_batch=x, feat_batch=f, dropout1=dp, dropout2=dp)
            if np.any(y):
                feed[self.labels_placeholder] = y
                loss, preds = session.run(
                    [self.loss, self.predictions], feed_dict=feed)
                losses.append(loss)
            else:
                preds = session.run(self.predictions, feed_dict=feed)
            predicted_indices = preds.argmax(axis=1)
            results.extend(predicted_indices)
        return np.mean(losses), results


def print_confusion(confusion, num_to_tag):
    """Helper method that prints confusion matrix."""
    # Summing top to bottom gets the total number of tags guessed as T
    total_guessed_tags = confusion.sum(axis=0)
    # Summing left to right gets the total number of true tags
    total_true_tags = confusion.sum(axis=1)
    print()
    print(confusion)
    for i, tag in sorted(num_to_tag.items()):
        prec = confusion[i, i] / float(total_guessed_tags[i])
        recall = confusion[i, i] / float(total_true_tags[i])
        print('Tag: {} - P {:2.4f} / R {:2.4f}'.format(tag, prec, recall))


def calculate_confusion(config, predicted_indices, y_indices):
    """Helper method that calculates confusion matrix."""
    confusion = np.zeros((config.label_size, config.label_size), dtype=np.int32)
    for i in range(len(y_indices)):
        correct_label = y_indices[i]
        guessed_label = predicted_indices[i]
        confusion[correct_label, guessed_label] += 1
    return confusion


def NER_learning(filename_params, filename_tf, config=None):
    """NER model implementation.
    """
    if config is None:
        config = Config()
    if not config.train_embedding:
        if not config.pre_embedding:
            raise Exception('Not train embedding allowed for pre-embedding only')
        # elif config.pre_embedding_from_file == '':
        #     raise Exception('Not train pre-embedding allowed only from file')
    with tf.Graph().as_default():
        model = NERModel({'config': config})
        print('data loaded')
        output_file = open(filename_params, 'wb')
        pickle.dump({'words': model.word_to_num, 'tags': model.tag_to_num, 'config': model.config},
                    output_file, protocol=3)
        output_file.close()
        init = tf.initialize_all_variables()
        # var_for_saving = {'Layer1/W:0', 'Layer1/b1:0', 'Layer1/Wf:0', 'Layer2/U:0', 'Layer2/b2:0'}
        var_for_saving = {}
        for v in tf.trainable_variables():
            var_for_saving[v.name] = v
        saver = tf.train.Saver(var_for_saving)

        with tf.Session() as session:
            best_val_loss = float('inf')
            best_val_epoch = 0

            session.run(init)
            for epoch in range(config.max_epochs):
                print('Epoch {}'.format(epoch))
                start = time.time()
                ###
                train_loss, train_acc = model.run_epoch(session, model.X_train,
                                                    model.y_train, model.feat_train)
                val_loss, predictions = model.predict(session, model.X_dev, model.y_dev, model.feat_dev)
                print('--------')
                print ('Training loss: {}'.format(train_loss))
                print ('Training acc: {}'.format(train_acc))
                print ('Validation loss: {}'.format(val_loss))
                print('--------')
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_val_epoch = epoch
                    # model_for_saving = {}
                    # model_for_saving['W'] =
                    # save_session(session, filename_tf)
                    saver.save(session, filename_tf)
                if epoch - best_val_epoch > config.early_stopping:
                    break
                ###
                confusion = calculate_confusion(config, predictions, model.y_dev)
                print_confusion(confusion, model.num_to_tag)
                print('Total time: {}'.format(time.time() - start))


def NER_predict(doc, settings, session_db=None, commit_session=True, verbose=False):

    values = {}
    for model_type in settings:
        NER_config = Config()
        learn_class = NER_config.classes[model_type['class']]
        # NER_config.feature_type = feature.ner_feature_types[learn_class + '_answers']
        # if model_type['use_special_tags']:
        #     list_tags = NER_config.special_tag_types[learn_class][model_type['tags']]
        # else:
        #     list_tags = NER_config.tag_types[model_type['tags']]
        #
        # NER_config.feature_answer = [learn_class + '_' + i for i in list_tags]
        filename_part = str(model_type['class']
                            ) + '_' + str(model_type['tags']
                            ) + '_' + str(model_type['use_special_tags'])
        filename_tf = home_dir + '/weights/ner_oc_' + filename_part + '.weights'
        filename_params = home_dir + '/weights/ner_oc_' + filename_part + '.params'

        NER_predict_set(doc, filename_params, filename_tf, values, session_db, commit_session, verbose=verbose)
        if verbose:
            print(values)
        if len(values) > 0:
            db.put_ner_feature_dict(doc.doc_id, values, feature.ner_feature_types[learn_class + '_predictions'],
                                    None, session_db, commit_session)


def NER_predict_set(doc, filename_params, filename_tf, values, session_db, commit_session=True, verbose=False):

    input_file = open(filename_params, 'rb')
    params = pickle.load(input_file)
    input_file.close()
    params['config'].doc = doc
    params['config'].new_model = False
    with tf.Graph().as_default():
        print('before Model', time.clock())
        model = NERModel(params, session=session_db)
        print('after Model', time.clock())

        init = tf.initialize_all_variables()
        var_for_saving = {}
        for v in tf.trainable_variables():
            var_for_saving[v.name] = v
        saver = tf.train.Saver(var_for_saving)
        var_for_init = []
        for v in tf.all_variables():
            if v.name == 'Embedding:0':
                if v.name not in var_for_saving.keys():
                    var_for_init.append(v)
        op_init = tf.initialize_variables(var_for_init)

        with tf.Session() as session:

            saver.restore(session, filename_tf)

            session.run(op_init)

            print('dev: lemma, answer, ner answer')
            print('=-=-=')
            _, predictions = model.predict(session, model.X_test, np.ones(len(model.X_test), dtype=int), features=model.feat_test)

        # num_to_word = {v: k for k, v in model.word_to_num.items()}
        num_to_tag = {v: k for k, v in model.tag_to_num.items()}
        # for i in range(len(predictions)):
        #     print([num_to_word[j] for j in model.X_test[i]], num_to_tag[predictions[i]])

        for i in range(len(predictions)):
            if not (predictions[i] == 0):
                values[(int(model.indexes[i][0]), int(model.indexes[i][1]), num_to_tag[predictions[i]])] = [1]
    if verbose:
        print(values)


def NER_person_learning():

    # training_set = u'1fe7391a-c5b9-4a07-bb6a-e6e4c5211008'
    # dev_set = u'97106298-d85e-4602-803f-a3c54685ada6'
    training_set = u'4fb42fd1-a0cf-4f39-9206-029255115d01'
    dev_set = u'f861ee9d-5973-460d-8f50-92fca9910345'

    if not os.path.exists(home_dir + "/weights"):
        os.makedirs(home_dir + "/weights")

    NER_config = Config()
    NER_config.training_set = training_set
    NER_config.dev_set = dev_set

    feature_count = 1
    # feature_count = 2
    for i in range(1, feature_count + 1):

        if i == 1:
            # NER_config.feature_answer = ['oc_span_last_name', 'oc_span_first_name', 'oc_span_middle_name',
            #                              'oc_span_nickname', 'oc_span_foreign_name']

            # NER_config.feature_answer = ['name_B', 'name_S', 'name_I', 'name_E']
            # NER_config.feature_answer = ['name_BS', 'name_IE']
            NER_config.feature_answer = ['name_BI', 'name_ES']
            # NER_config.feature_answer = ['person_BS', 'person_IE']
            # NER_config.feature_answer = ['person_BI', 'person_ES']

            filename_tf = home_dir + '/weights/ner_oc1.weights'
            filename_params = home_dir + '/weights/ner_oc1.params'

        else:
            NER_config.feature_answer = ['oc_span_post', 'oc_span_role', 'oc_span_status']
            #NER_config.feature_answer = ['post_role_status_B', 'post_role_status_S',
            #                             'post_role_status_I', 'post_role_status_E']

            filename_tf = home_dir + '/weights/ner_oc2.weights'
            filename_params = home_dir + '/weights/ner_oc2.params'

        NER_learning(filename_params, filename_tf, NER_config)


def NER_name_learning():

    if not os.path.exists(home_dir + "/weights"):
        os.makedirs(home_dir + "/weights")

    NER_config = Config()
    NER_config.learn_type['class'] = 1
    NER_config.learn_type['tags'] = 1
    learn_class = NER_config.classes[NER_config.learn_type['class']]
    NER_config.feature_type = feature.ner_feature_types[learn_class + '_answers']
    NER_config.feature_answer = [learn_class + '_' + i for i in NER_config.tag_types[NER_config.learn_type['tags']]]
    filename_part = str(NER_config.learn_type['class']) + '_' + str(NER_config.learn_type['tags'])
    filename_tf = home_dir + '/weights/ner_oc_' + filename_part + '.weights'
    filename_params = home_dir + '/weights/ner_oc_' + filename_part + '.params'

    training_set = u'4fb42fd1-a0cf-4f39-9206-029255115d01'
    dev_set = u'f861ee9d-5973-460d-8f50-92fca9910345'

    NER_config.training_set = training_set
    NER_config.dev_set = dev_set

    # print(NER_config.feature_answer)

    NER_learning(filename_params, filename_tf, NER_config)


def NER_learning_by_config(NER_settings):
    # 4. Обучение и запись модели в файл
    if not os.path.exists(home_dir + "/weights"):
        os.makedirs(home_dir + "/weights")

    NER_config = Config()
    NER_config.learn_type = NER_settings

    learn_class = NER_config.classes[NER_config.learn_type['class']]
    NER_config.feature_type = feature.ner_feature_types[learn_class + '_answers']
    NER_config.feature_answer = [learn_class + '_' + i for i in NER_config.tag_types[NER_config.learn_type['tags']]]

    NER_config.training_set = sets[learn_class]['train']
    NER_config.dev_set = sets[learn_class]['dev']

    # print(NER_config.feature_answer)

    filename_part = str(NER_settings['class']
                        ) + '_' + str(NER_settings['tags']
                                      ) + '_' + str(NER_settings['use_special_tags'])
    filename_tf = home_dir + '/weights/ner_oc_' + filename_part + '.weights'
    filename_params = home_dir + '/weights/ner_oc_' + filename_part + '.params'

    NER_learning(filename_params, filename_tf, NER_config)