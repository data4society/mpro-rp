from mprorp.tomita.tomita_run import run_tomita
from mprorp.celery_app import app
from mprorp.ner.regular import regular_entities

grammars = ['date.cxx', 'person.cxx']
grammar_count = 2
facts = ['Person']


@app.task
def regular_tomita(grammar_index, doc_id):
    run_tomita(grammars[grammar_index], doc_id, 10 + grammar_index)
    if grammar_index == 0:
        regular_tomita.delay(1, doc_id)
    if grammar_index == 1:
        regular_entities.delay(doc_id)
