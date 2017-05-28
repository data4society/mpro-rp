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
from sqlalchemy import or_

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
        create_tr_and_test_sets('2' + str(i), neg_list)


def set_train_and_test_pp_ss():
    neg_list = list(db.get_set_docs(set_list.sets['negative']['all2']))
    print(len(neg_list))
    random.shuffle(neg_list)

    for i in ['pp', 'ss']:
        create_tr_and_test_sets(i, neg_list)


def create_tr_and_test_sets(key, neg_list):
        pos_docs = list(db.get_set_docs(set_list.sets[key]['positive']))
        random.shuffle(pos_docs)
        pos_len = len(pos_docs)
        tr_len = round(pos_len * 0.8)
        tr_set = pos_docs[:tr_len]
        test_set = pos_docs[tr_len:]
        if len(neg_list) < pos_len:
            tr_neg_len = round(len(neg_list) * .8)
            tr_set.extend(neg_list[:tr_neg_len])
            test_set.extend(neg_list[tr_neg_len:])
        else:
            tr_neg_len = tr_len
            tr_set.extend(neg_list[:tr_len])
            test_set.extend(neg_list[tr_len:pos_len])
        print(key, str(tr_len), len(tr_set), 'train', db.put_training_set(tr_set, key + ' train 26.05.17 pos=' + str(tr_len) + ' neg=' + str(tr_neg_len)))
        print(key, str(pos_len - tr_len), len(test_set), 'test', db.put_training_set(test_set, key + ' test 26.05.17 pos=' + str(pos_len - tr_len)))


def add_rubric_to_docs(rubric_id, doc_ids, session=None):
    if session is None:
        session = Driver.db_session()
    for doc_id in doc_ids:
        session.query(DocumentRubric).filter((DocumentRubric.rubric_id == rubric_id) &
                                             (DocumentRubric.doc_id == doc_id)).delete()
        new_id = DocumentRubric(doc_id=doc_id, rubric_id=rubric_id)
        session.add(new_id)
    session.commit()


def put_rubric_answers():
    for i in range(1,7):
        docs = db.get_set_docs(set_list.sets['2' + str(i)]['new'])
        rub_id = set_list.rubrics[str(i)]['pos']
        add_rubric_to_docs(rub_id, docs)


def pp_ss_positive_sets():
    for key in ['pp', 'ss']:
        rub_id = set_list.rubrics[key]['pos']
        set_answers_new_sets(rub_id)


def set_answers_new_sets(rub_id):
    docs = session.query(Document.doc_id, Document.rubric_ids).filter(Document.status.in_([74])).all()
    set_pos = []
    for i in docs:
        if i.rubric_ids is not None:
            for id in i.rubric_ids:
                if str(id) == rub_id:
                    set_pos.append(str(i.doc_id))
    add_rubric_to_docs(rub_id, set_pos)
    print(len(set_pos))


def create_pp_ss_positive_sets():
    for key, name in [('pp', 'Политпрессинг'), ('ss', 'Свобода собраний')]:
        rub_id = set_list.rubrics[key]['pos']
        create_set_from_doc_rubrics(rub_id, name)


def create_set_from_doc_rubrics(rubric_id, name):
    docs = session.query(DocumentRubric.doc_id).filter((DocumentRubric.rubric_id == rubric_id)).all()
    doc_set = [str(i) for (i,) in docs]
    # print(doc_set[0])
    print(name, len(doc_set), db.put_training_set(doc_set, name + ' Позитив 26.05.17'))


def new_negative():
    docs = list(db.get_set_docs(set_list.sets['negative']['new2']))
    docs2 = list(db.get_set_docs(set_list.sets['negative']['all']))
    docs.extend(docs2)
    print(db.put_training_set(docs, 'negativ new2'))



def test():
    docs = db.get_set_docs(set_list.sets['negative']['new2'])
    docs2 = db.get_set_docs(set_list.sets['negative']['all'])
    yes = 0
    no = 0
    for doc_id in docs:
        if doc_id in docs2:
            yes += 1
        else:
            no += 1
    print(yes, no, len(docs), len(docs2))


def script_exec():
    docs_74 = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=77).all()
    count = 0
    count_skip = 0
    for item in docs_74:
        count += 1
        if count < count_skip:
            continue
        doc = session.query(Document).filter(Document.doc_id == item.doc_id).one()
        rb.morpho_doc(doc)
        rb.lemmas_freq_doc(doc)
        ner_feature.create_embedding_feature(doc, session=session, commit_session=False)
        if count % 100 == 0:
            session.commit()
            print('count', count)
    print('for - end. Last commit')
    session.commit()
    print('count', count)


# put_rubric_answers()
# pp_ss_positive_sets()
# create_pp_ss_positive_sets()
set_train_and_test_pp_ss()
# new_negative()