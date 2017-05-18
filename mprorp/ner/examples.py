from mprorp.tomita.regular import grammar_count
import mprorp.analyzer.db as db
import mprorp.ner.NER as NER
import mprorp.analyzer.rubricator as rb
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import mprorp.ner.morpho_to_vec as mystem_to_vec
import os
import mprorp.ner.tomita_to_markup as tomita_to_markup
from mprorp.tomita.tomita_run import run_tomita2
from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.ner.identification import create_answers_feature_for_doc_2

import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from mprorp.analyzer.db import put_training_set
from gensim.models import word2vec
from mprorp.utils import home_dir
import tensorflow as tf


session = Driver.db_session()

batch_size = 128
reg_coef = 0.005
lr=10
tf_steps = 100


def create_rubric_train_data(tr_set, rubric_id, embedding_id, verbose=False):
    embeds = db.get_docs_embedding(embedding_id, tr_set)
    # doc_ids = []
    emb_list = []
    ans_list = []
    answers = db.get_rubric_answers(tr_set, rubric_id)
    if verbose:
        print('answers: ', len(answers), sum(list(answers.values())))
    for doc_id in embeds:
        # doc_ids.append(doc_id)
        emb_list.append(embeds[doc_id])
        ans_list.append(answers[doc_id])
    return emb_list, ans_list


def run_rubric_model(tr_data, labels, embedding_size):

    graph = tf.Graph()

    with graph.as_default(), tf.device('/cpu:0'):
        # Input data.
        train_dataset = tf.placeholder(tf.float32, shape=[batch_size, embedding_size])
        train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])

        # Variables.
        weights = tf.Variable(tf.random_uniform([embedding_size, 1], -1.0, 1.0))
        # tf.add_to_collection('total_loss', 0.5 * reg_softmax * tf.nn.l2_loss(weights))
        bias = tf.Variable(0.00001)

        y = tf.matmul(train_dataset, weights) + bias

        cross_entropy_array = tf.log(tf.sigmoid(y)) * train_labels + tf.log(1 - tf.sigmoid(y)) * (1 - train_labels)

        cross_entropy = - tf.reduce_mean(cross_entropy_array) + tf.reduce_mean(weights * weights) * reg_coef

        train_step = tf.train.GradientDescentOptimizer(learning_rate=lr).minimize(cross_entropy)
        init = tf.initialize_all_variables()

        sess = tf.Session()
        sess.run(init)

        for i in range(tf_steps):
            sess.run(train_step, feed_dict={train_dataset: tr_data, train_labels: labels})

    model = weights.eval(sess)[:, 0]
    model = model.tolist()
    model.append(float(bias.eval(sess)))