"""learning phase of fastart controller"""
import datetime
import sys
sys.path.append('../..')
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.analyzer.fasttext_rubrication import compute_embedding, learning, get_answer
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import load_only
from mprorp.fastart.celery_app import app
from celery import group
from mprorp.config.settings import learning_parameters as lp

fasttext_params = lp['fasttext']
DOCS_TO_STEP = fasttext_params['docs_to_step']
MARKING_STEPS_NUM = fasttext_params['marking_steps_num']


#@app.task(ignore_result=True)
def create_model(rubric_id):
    """create model by bad and good docs"""
    session = db_session()
    rubric = session.query(FastartRubric).filter_by(rubric_id = rubric_id).first()
    docs = rubric.docs
    all = docs["all"]
    marked = [doc for doc in all if doc["answer"] > 0 and doc["answer"]%3 != 0]
    embeddings = []
    answers = []
    for doc in marked:
        stripped = session.query(Document.stripped).filter_by(doc_id = doc["doc_id"]).first()[0]
        embeddings.append(compute_embedding(stripped))
        answers.append(2-doc["answer"])
    model_filename = 'fasttext_'+rubric_id+'_'+str(datetime.datetime.now()).replace(' ','_').replace('.','_')
    model = learning(embeddings, answers, model_filename)
    print("learning_complete")
    docs["all"], rubric.doc_ind = sort_docs(all, model, session)
    flag_modified(rubric, "docs")
    print("sorting_complete")
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
    answers_for_news = {}
    doc_ids = [doc["doc_id"] for doc in new]
    docs = session.query(Document).options(load_only("doc_id", "stripped")).filter(Document.doc_id.in_(doc_ids)).all()
    tasks_list = []
    for doc in docs:
        doc_id = str(doc.doc_id)
        stripped = doc.stripped
        tasks_list.append(get_answer_task.s(model, stripped, doc_id))
    new_group = group(tasks_list)
    results = new_group()
    results.get()
    for doc_id, ans in results:
        answers_for_news[doc_id] = ans

    #for doc in new:
    #    doc_id = doc["doc_id"]
    #    stripped = session.query(Document.stripped).filter(doc_id = doc_id).first()[0]
    new = sorted(new, key=lambda doc: abs(answers_for_news[doc["doc_id"]]-0.5))
    return old+new, i


@app.task(ignore_result=False)
def get_answer_task(model, txt, doc_id):
    """get probability answer for doc by model"""
    return doc_id, get_answer(model, txt)
