from mprorp.db.dbDriver import *
from mprorp.db.models import *

import mprorp.analyzer.rubricator as rb
from mprorp.tomita.tomita_run import run_tomita
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup

from mprorp.celery_app import app


if "worker" in sys.argv:
    celery = True
else:
    celery = False


def router_func(doc_id, status):
    print("route:", doc_id, status)
    if status == 0:
        pass
    if status == 1:
        doc_id = str(doc_id)
        regular_morpho.delay(doc_id)
    if status == 2:
        regular_lemmas.delay(doc_id)
    if status == 3:
        regular_rubrication.delay(doc_id)
    if status == 4:
        doc = Document(doc_id = doc_id, status = 1000)
        update(doc)


status = {'morpho': 2, 'lemmas': 3, 'rubrics': 4}
rubrics_for_regular = {u'76819d19-d3f7-43f1-bc7f-b10ec5a2e2cc': u'404f1c89-53bd-4313-842d-d4a417c88d67'}  # 404f1c89-53bd-4313-842d-d4a417c88d67


@app.task
def regular_morpho(doc_id):
    rb.morpho_doc(doc_id, status['morpho'])
    router_func(doc_id, 2)


# counting lemmas frequency for one document
@app.task
def regular_lemmas(doc_id):
    rb.lemmas_freq_doc(doc_id, status['lemmas'])
    router_func(doc_id, 3)


# regular ribrication
@app.task
def regular_rubrication(doc_id):
    rb.spot_doc_rubrics(doc_id, rubrics_for_regular, status['rubrics'])
    # router_func(doc_id, 4)
    regular_tomita(0, doc_id)


grammars = ['date.cxx', 'person.cxx']
facts = ['Person']

@app.task
def regular_tomita(grammar_index, doc_id):
    run_tomita(grammars[grammar_index], doc_id, 10 + grammar_index)
    if grammar_index == 0:
        regular_tomita.delay(1, doc_id)
    if grammar_index == 1:
        regular_entities.delay(doc_id)


@app.task
def regular_entities(doc_id):
    convert_tomita_result_to_markup(doc_id, ['person.cxx'])
    doc = Document(doc_id=doc_id, status=1000)
    update(doc)