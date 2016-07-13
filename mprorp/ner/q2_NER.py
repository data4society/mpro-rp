import os
import getpass
import sys
import time

import numpy as np
import tensorflow as tf
from mprorp.ner.q2_initialization import xavier_weight_init
import mprorp.ner.data_utils.utils as du
import mprorp.ner.data_utils.ner as ner
from mprorp.ner.utils import data_iterator
from mprorp.ner.model import LanguageModel
import mprorp.analyzer.db as db
from mprorp.ner.config import features_size

class Config(object):
    """Holds model hyperparams and data information.

    The config class is used to store various hyperparameters and dataset
    information parameters. Model objects are passed a Config() object at
    instantiation.
    """
    embed_size = 300
    batch_size = 64
    label_size = 5
    hidden_size = 500
    max_epochs = 24
    early_stopping = 2
    dropout = 0.9
    lr = 0.001
    l2 = 0.001
    window_size = 5
    training_set = u'199698a2-e3f4-48a8-aaaa-09778161c8c4'
    dev_set = u'074c809b-208c-4fb4-851c-1e71d7f01b60'
    pre_embedding = True
    embedding = 'first_test_embedding'
    feature_answer = 'person_answer'
    # feature_answer = 'org_answer'
    # features = []
    features = ['Org', 'Person', 'morpho']
    print(features)
    features_length = 0
    for feat in features:
        features_length += features_size[feat]


class NERModel(LanguageModel):
    """Implements a NER (Named Entity Recognition) model.

    This class implements a deep network for named entity recognition. It
    inherits from LanguageModel, which has an add_embedding method in addition to
    the standard Model method.
    """

    def load_data_db(self, debug=False):
        """Loads starter word-vectors and train/dev/test data."""
        # Load the starter word vectors
        training_set = self.config.training_set
        #  train_set_words[doc_id] = [(sentence, word, [lemma1, lemma2]), ... (...)]
        train_set_words = db.get_ner_feature_for_set(training_set, 'embedding')

        # collect words from set

        words_for_embedding = {}
        for doc_id in train_set_words:
            doc_words = train_set_words[doc_id]
            for element in doc_words:
                for word in element[2]:
                    words_for_embedding[word] = ''

        wv_dict = db.get_multi_word_embedding(self.config.embedding, words_for_embedding.keys())

        # Create word_to_num and LookUp table (wv)

        wv_array = [np.random.uniform(-0.1, 0.1, 300)]

        word_to_num = {'UUUNKKK': 0}
        count = 1
        for word in wv_dict:
            word_to_num[word] = count
            wv_array.append(wv_dict[word])
            count += 1

        # If word not in wv_dict (in embedding) we change it with 'UUUNKKK' = 0
        # We can append random array for such word

        self.wv = np.array(wv_array, dtype=np.float32)
        # refs[doc_if] = [(start_offset, end_offset, entity_class)]
        # refs = db.get_references_for_set(training_set)

        # refs -> answers:
        # for doc_id in refs:
        #     for word in train_set_words[doc_id]:

        answers = db.get_ner_feature_for_set_dict(training_set, self.config.feature_answer)

        tagnames = [0]
        for doc_id in answers:
            for key in answers[doc_id]:
                ans = answers[doc_id][key]
                ans_tuple = (ans[0], ans[1])
                if not (ans_tuple in tagnames):
                    tagnames.append(ans_tuple)

        self.config.label_size = len(tagnames)
        # tagnames = [0, ('person', 'B'), ('person', 'I'), ('person', 'E'), ('person', 'S'),
        #                ('org', 'B'), ('org', 'I'), ('org', 'E'), ('org', 'S')]
        self.num_to_tag = dict(enumerate(tagnames))
        tag_to_num = {v: k for k, v in iter(self.num_to_tag.items())}

        features_set = {}
        for feat in self.config.features:
            features_set[feat] = db.get_ner_feature_for_set_dict(training_set, feat)

        self.feat_train, self.X_train, self.y_train, _ = du.docs_to_windows2(train_set_words, word_to_num,
                                                        tag_to_num, answers,
                                                        self.config.features,
                                                        features_set, features_size, self.config.features_length,
                                                        wsize=self.config.window_size)

        dev_set = self.config.dev_set
        #  train_set_words[doc_id] = [(sentence, word, [lemma1, lemma2]), ... (...)]
        dev_set_words = db.get_ner_feature_for_set(dev_set, 'embedding')
        answers = db.get_ner_feature_for_set_dict(dev_set, self.config.feature_answer)
        features_set = {}
        for feat in self.config.features:
            features_set[feat] = db.get_ner_feature_for_set_dict(dev_set, feat)
        self.feat_dev, self.X_dev, self.y_dev, self.w_dev = du.docs_to_windows2(dev_set_words, word_to_num,
                                                         tag_to_num, answers,
                                                         self.config.features,
                                                         features_set, features_size, self.config.features_length,
                                                         wsize=self.config.window_size)

        print("Размер учебной выборки: ", len(self.X_train))

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
        self.dropout_placeholder = tf.placeholder(tf.float32, name='Dropout')
        ### END YOUR CODE

    def create_feed_dict(self, input_batch, dropout, label_batch=None, feat_batch=None):
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
        if dropout is not None:
            feed_dict[self.dropout_placeholder] = dropout
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
                embedding = tf.Variable(self.wv, name='Embedding')
            else:
                embedding = tf.get_variable('Embedding', [len(self.wv), self.config.embed_size])
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

            if self.config.l2:
                tf.add_to_collection('total_loss', 0.5 * self.config.l2 * tf.nn.l2_loss(W))

        with tf.variable_scope('Layer2', initializer=xavier_weight_init()) as scope:
            U = tf.get_variable('U', [self.config.hidden_size, self.config.label_size])
            b2 = tf.get_variable('b2', [self.config.label_size])
            y = tf.matmul(h, U) + b2
            if self.config.l2:
                tf.add_to_collection('total_loss', 0.5 * self.config.l2 * tf.nn.l2_loss(U))
        output = tf.nn.dropout(y, self.dropout_placeholder)
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

    def __init__(self, config):
        """Constructs the network using the helper functions defined above."""
        self.config = config
        # self.load_data(debug=False)
        self.load_data_db(debug=False)
        self.add_placeholders()
        window = self.add_embedding(config.pre_embedding)
        y = self.add_model(window)

        self.loss = self.add_loss_op(y)
        self.predictions = tf.nn.softmax(y)
        one_hot_prediction = tf.argmax(self.predictions, 1)
        correct_prediction = tf.equal(
            tf.argmax(self.labels_placeholder, 1), one_hot_prediction)
        self.correct_predictions = tf.reduce_sum(tf.cast(correct_prediction, 'int32'))
        self.train_op = self.add_training_op(self.loss)

    def run_epoch(self, session, input_data, input_labels, input_features, shuffle=True, verbose=True):
        orig_features, orig_X, orig_y = input_features, input_data, input_labels
        dp = self.config.dropout
        # We're interested in keeping track of the loss and accuracy during training
        total_loss = []
        total_correct_examples = 0
        total_processed_examples = 0
        total_steps = len(orig_X) / self.config.batch_size
        for step, (x, y, f) in enumerate(
            data_iterator(orig_X, orig_y, orig_features, batch_size=self.config.batch_size,
                       label_size=self.config.label_size, shuffle=shuffle)):
            feed = self.create_feed_dict(input_batch=x, dropout=dp, label_batch=y, feat_batch=f)
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
            feed = self.create_feed_dict(input_batch=x, feat_batch=f, dropout=dp)
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


def save_predictions(predictions, filename):
    """Saves predictions to provided file."""
    with open(filename, "wb") as f:
        for prediction in predictions:
            f.write(str(prediction) + "\n")


def test_NER():
    """Test NER model implementation.

    You can use this function to test your implementation of the Named Entity
    Recognition network. When debugging, set max_epochs in the Config object to 1
    so you can rapidly iterate.
    """
    config = Config()
    with tf.Graph().as_default():
        model = NERModel(config)

        init = tf.initialize_all_variables()
        saver = tf.train.Saver()

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
                print ('Training loss: {}'.format(train_loss))
                print ('Training acc: {}'.format(train_acc))
                print ('Validation loss: {}'.format(val_loss))
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_val_epoch = epoch
                    if not os.path.exists("./weights"):
                        os.makedirs("./weights")

                    saver.save(session, './weights/ner.weights')
                if epoch - best_val_epoch > config.early_stopping:
                    break
                ###
                confusion = calculate_confusion(config, predictions, model.y_dev)
                print_confusion(confusion, model.num_to_tag)
                print('Total time: {}'.format(time.time() - start))

            saver.restore(session, './weights/ner.weights')
            print('dev: lemma, answer, ner answer')
            print('=-=-=')
            # print('Writing predictions to q2_test.predicted')
            _, predictions = model.predict(session, model.X_dev, model.y_dev, model.feat_dev)
            for i in range(len(model.w_dev)):
                print(model.w_dev[i], model.num_to_tag[model.y_dev[i]], model.num_to_tag[predictions[i]])
            # save_predictions(predictions, "q2_test.predicted")

if __name__ == "__main__":
    test_NER()
