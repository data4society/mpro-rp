import datetime
import sys
sys.path.append('../..')
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.analyzer.fasttext_rubrication import compute_embedding, learning, get_answer
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import load_only

def create_model(rubric_id):
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
    rubric.step+=1
    session.commit()
    session.close()

answers_for_new = {}
def sorting_func(doc):
    ans = answers_for_new[doc["doc_id"]]
    return abs(ans-0.5)

def sort_docs(docs, model, session):
    global answers_for_new
    i = 0
    for doc in docs:
        if doc["answer"] == -1:
            break
        i+=1
    old = docs[:i]
    new = docs[i:200]
    answers_for_new = {}
    doc_ids = [doc["doc_id"] for doc in new]
    docs = session.query(Document).options(load_only("doc_id", "stripped")).filter(Document.doc_id.in_(doc_ids)).all()
    for doc in docs:
        doc_id = str(doc.doc_id)
        stripped = doc.stripped
        answers_for_new[doc_id] = get_answer(model, stripped)
    #for doc in new:
    #    doc_id = doc["doc_id"]
    #    stripped = session.query(Document.stripped).filter(doc_id = doc_id).first()[0]
    #    answers_for_new[doc_id] = get_answer(model, stripped)
    new.sort(key=sorting_func)
    return old+new, i
