from mprorp.celery_app import app
# from mprorp.controller.logic import router_func

from mprorp.tomita.regular import regular_tomita
import mprorp.analyzer.rubricator as rb

status = {'morpho': 2, 'lemmas': 3, 'rubrics': 4}
rubrics_for_regular = {u'76819d19-d3f7-43f1-bc7f-b10ec5a2e2cc': u'404f1c89-53bd-4313-842d-d4a417c88d67'}  # 404f1c89-53bd-4313-842d-d4a417c88d67

@app.task
def regular_morpho(doc_id):
    rb.morpho_doc2(doc_id, status['morpho'])
    # router_func(doc_id, 2)
    regular_lemmas.delay(doc_id)


# counting lemmas frequency for one document
@app.task
def regular_lemmas(doc_id):
    rb.lemmas_freq_doc2(doc_id, status['lemmas'])
    # router_func(doc_id, 3)
    regular_rubrication.delay(doc_id)


# regular ribrication
@app.task
def regular_rubrication(doc_id):
    rb.spot_doc_rubrics2(doc_id, rubrics_for_regular, status['rubrics'])
    # router_func(doc_id, 4)
    regular_tomita(0, doc_id)