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
import mprorp.ner.set_list as set_list

import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from mprorp.analyzer.db import put_training_set
from gensim.models import word2vec
from mprorp.utils import home_dir
import tensorflow as tf
import mprorp.ner.feature as ner_feature
import random

session = Driver.db_session()


def sets_from_new_accepted_docs():
    docs_74 = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=74).all()
    print('all 74', len(docs_74))
    rubs = {}
    lens = [0 for i in range(9)]
    neg_set = []
    for item in docs_74:
        lens[len(item.rubric_ids)] += 1
        if len(item.rubric_ids) == 0:
            neg_set.append(str(item.doc_id))
        else:
            for rub in item.rubric_ids:
                if rubs.get(str(rub), None) is None:
                    rubs[str(rub)] = []
                rubs[str(rub)].append(item.doc_id)
    rub_keys = {set_list.rubrics[i]['pos']: i for i in set_list.rubrics}
    rub_names_db = session.query(Rubric.rubric_id, Rubric.name).all()
    rub_names = {str(i.rubric_id):i.name for i in rub_names_db}
    for rub in rubs:
        set_id = db.put_training_set(rubs[rub], rub_names[rub] + ' new 26.05.17')
        print(rub_keys[rub], rub_names[rub], len(rubs[rub]))
        print(set_id)
    set_id = db.put_training_set(neg_set, 'negative new 26.05.17')
    print('negative new 26.05.17', len(neg_set))
    print(set_id)


def sets_with_new_docs():
    for i in range(1, 7):
        new_docs = list(db.get_set_docs(set_list.sets['2' + str(i)]['new']))
        pos_docs = list(db.get_set_docs(set_list.sets['1' + str(i)]['positive']))
        pos_docs.extend(new_docs)
        # print(i, len(new_docs), len(pos_docs), len(set(pos_docs)))
        print(i, db.put_training_set(pos_docs, str(i) + ' positive 26.05.17'))


def set_train_and_test():
    neg_list = list(db.get_set_docs(set_list.sets['negative']['all']))
    print(len(neg_list))
    random.shuffle(neg_list)

    for i in range(1, 7):
        pos_docs = list(db.get_set_docs(set_list.sets['2' + str(i)]['positive']))
        random.shuffle(pos_docs)
        pos_len = len(pos_docs)
        tr_len = round(pos_len * 0.8)
        tr_set = pos_docs[:tr_len]
        tr_set.extend(neg_list[:tr_len])
        print(i, str(tr_len), 'train', db.put_training_set(tr_set, str(i) + ' train 26.05.17 pos=neg=' + str(tr_len)))
        test_set = pos_docs[tr_len:]
        test_set.extend(neg_list[tr_len:pos_len])
        print(i, str(pos_len - tr_len), 'test', db.put_training_set(tr_set, str(i) + ' test 26.05.17 pos=neg=' + str(pos_len - tr_len)))


def test():
    docs = db.get_set_docs(set_list.sets['11']['new'])
    docs2 = db.get_set_docs(set_list.sets['11']['positive'])
    yes = 0
    no = 0
    for doc_id in docs:
        if doc_id in docs2:
            yes += 1
        else:
            no += 1
    print(yes, no)


def script_exec():
    docs_74 = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=74).all()
    count = 0
    count_skip = 3900
    for item in docs_74:
        count += 1
        if count < count_skip:
            continue
        doc = session.query(Document).filter(Document.doc_id == item.doc_id).one()
        rb.morpho_doc(doc)
        rb.lemmas_freq_doc(doc)
        ner_feature.create_embedding_feature(doc, session=session, commit_session=False)
        if count % 10 == 0:
            session.commit()
            print('count', count)
    print('for - end. Last commit')
    session.commit()
    print('count', count)


set_train_and_test()