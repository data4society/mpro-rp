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
import mprorp.ner.feature as ner_feature

session = Driver.db_session()


def script_exec2():
    docs_74 = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=74).all()
    print('all 74', len(docs_74))
    rubs = {}
    lens = [0 for i in range(9)]
    for item in docs_74:
        lens[len(item.rubric_ids)] += 1
        for rub in item.rubric_ids:
            rubs[str(rub)] = rubs.get(str(rub), 0) + 1
    print(lens)
    print(rubs)


def script_exec():
    docs_74 = session.query(Document.doc_id, Document.rubric_ids).filter_by(status=74).all()
    count = 0
    count_skip = 460
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


script_exec()