"""learning phase of fastart controller"""
import logging
import sys
import numpy as np
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', filename = u'/home/mprorp/mpro-rp-dev/fastart.txt')
root = logging.getLogger()
root.setLevel(logging.DEBUG)

import datetime
sys.path.append('../..')
from mprorp.fastart.fastart_app import cel_app
if 'fastart_app.py' not in sys.argv:
    logging.info("LC INIT START")
    from mprorp.db.dbDriver import *
    from mprorp.db.models import *
    from mprorp.analyzer.fasttext_rubrication import compute_embedding, learning, get_answer
    from sqlalchemy.orm.attributes import flag_modified
    from sqlalchemy.orm import load_only
    from celery import group
    from celery.result import allow_join_result
    from mprorp.config.settings import learning_parameters as lp
    fasttext_params = lp['fasttext']
    DOCS_TO_STEP = fasttext_params['docs_to_step']
    MARKING_STEPS_NUM = fasttext_params['marking_steps_num']
    logging.info("LC INIT COMPLETE")

@cel_app.task(ignore_result=True, time_limit=3660, soft_time_limit=3600)
def create_model(rubric_id):
    """create model by bad and good docs"""
    session = db_session()
    rubric = session.query(FastartRubric).filter_by(rubric_id = rubric_id).first()
    docs = rubric.docs
    all = docs["all"]
    marked = [doc for doc in all if doc["answer"] > 0 and doc["answer"]%3 != 0]
    doc_ids = [doc["doc_id"] for doc in marked]

    print("start get")
    doc_objs = session.query(Document).options(load_only("doc_id", "stripped")).filter(Document.doc_id.in_(doc_ids)).all()
    print("fin get")

    """
    with allow_join_result():
        tasks_list = [get_embedding.s(str(doc.doc_id),doc.stripped) for doc in doc_objs]
        new_group = group(tasks_list)
        tasks = new_group()
        results = tasks.get()
        results = {doc_id:np.array(ans) for doc_id, ans in results}
        for doc in marked:
            print(doc["doc_id"])
            print(results[doc["doc_id"]])
        embeddings = [results[doc["doc_id"]] for doc in marked]
        answers = [2-doc["answer"]%3 for doc in marked]
    """

    results = {str(doc.doc_id):compute_embedding(doc.stripped) for doc in doc_objs}
    embeddings = [results[doc["doc_id"]] for doc in marked]
    answers = [2-doc["answer"]%3 for doc in marked]

    model_filename = 'fasttext_'+rubric_id+'_'+str(datetime.datetime.now()).replace(' ','_').replace('.','_')
    print("learning_start")
    model = learning(embeddings, answers, model_filename)
    print("learning_complete")
    docs["all"], rubric.doc_ind = sort_docs(all, model, session)
    print("sorting_complete")
    flag_modified(rubric, "docs")
    rubric.step += 1
    if rubric.step == MARKING_STEPS_NUM:
        rubric.step = -1
    rubric.models = {'model_name': model_filename}

    session.commit()
    session.close()


def sort_docs(docs, model, session):
    """sort docs by answer's nearing to 0.5"""
    global answers_for_new
    i = 0
    for doc in docs:
        if doc["answer"] == -1:
            break
        i+=1

    old = docs[:i]
    new = docs[i:i+DOCS_TO_STEP]
    end = docs[i+DOCS_TO_STEP:]
    doc_ids = [doc["doc_id"] for doc in new]


    print("start get2")
    docs = session.query(Document).options(load_only("doc_id", "stripped")).filter(Document.doc_id.in_(doc_ids)).all()
    print("fin get2")


    with allow_join_result():
        tasks_list = [get_answer_task.s(model, doc.stripped, str(doc.doc_id)) for doc in docs]
        new_group = group(tasks_list)
        tasks = new_group()
        results = tasks.get()
        answers_for_news = {doc_id:ans for doc_id, ans in results}

    #for doc in new:
    #    doc_id = doc["doc_id"]
    #    stripped = session.query(Document.stripped).filter(doc_id = doc_id).first()[0]
    new = sorted(new, key=lambda doc: abs(answers_for_news[doc["doc_id"]]-0.5))
    return old+new+end, i


@cel_app.task(ignore_result=False)
def get_answer_task(model, txt, doc_id):
    """get probability answer for doc by model"""
    return doc_id, get_answer(model, txt)


@cel_app.task(ignore_result=False)
def get_embedding(doc_id, stripped):
    """get embedding for doc"""
    res = list(compute_embedding(stripped))
    return doc_id, res
