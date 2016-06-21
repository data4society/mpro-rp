from mprorp.db.dbDriver import *
from mprorp.db.models import *

import mprorp.analyzer.rubricator as rb
from mprorp.tomita.tomita_run import run_tomita
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup

from mprorp.celery_app import app

TO_MORPHO_STATUS = 100
TO_LEMMAS_STATUS = 101
TO_RUBRICATION_STATUS = 102
TO_MORPHO_STATUS = 200
TO_MORPHO_STATUS = 300
FINISH_STATUS = 1000

if "worker" in sys.argv:
    celery = True
else:
    celery = False

rubrics_for_regular = {u'76819d19-d3f7-43f1-bc7f-b10ec5a2e2cc': u'404f1c89-53bd-4313-842d-d4a417c88d67'}  # 404f1c89-53bd-4313-842d-d4a417c88d67
grammars = ['date.cxx', 'person.cxx']
facts = ['Person']

def router(doc_id, status):
    print("route:", doc_id, status)
    if status == 0:
        pass
    if status == 100:  # to morpho
        doc_id = str(doc_id)
        regular_morpho.delay(doc_id)
    if status == 101:  # to lemmas
        regular_lemmas.delay(doc_id)
    if status == 102:  # to rubrication
        regular_rubrication.delay(doc_id)
    if status >= 200 and status <= 200+len(grammars):  # to tomita
        regular_tomita(status-10, doc_id, status+1)
    if status == len(grammars)+1:  # to ner
        regular_entities(doc_id)
    if status == 300:  # fin regular processes
        doc = Document(doc_id = doc_id, status = 1000)
        update(doc)




@app.task
def regular_morpho(doc_id, new_status):
    rb.morpho_doc(doc_id, new_status)
    router(doc_id, new_status)


# counting lemmas frequency for one document
@app.task
def regular_lemmas(doc_id, new_status):
    rb.lemmas_freq_doc(doc_id, new_status)
    router(doc_id, new_status)


# regular rubrication
@app.task
def regular_rubrication(doc_id, new_status):
    rb.spot_doc_rubrics(doc_id, rubrics_for_regular, new_status)
    router(doc_id, new_status)


@app.task
def regular_tomita(grammar_index, doc_id, new_status):
    run_tomita(grammars[grammar_index], doc_id, new_status)
    router(doc_id, new_status)


@app.task
def regular_entities(doc_id, new_status):
    convert_tomita_result_to_markup(doc_id, ['person.cxx'])
    router(doc_id, new_status)