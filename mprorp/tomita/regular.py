# from mprorp.tomita.tomita_run import run_tomita2
# from mprorp.celery_app import app
# from mprorp.ner.regular import regular_entities
from mprorp.tomita.grammars.config import config
#
# # grammars = ['date.cxx', 'person.cxx']
grammars = config.keys()
grammar_count = len(grammars)
facts = config.values()
#
#
# @app.task
# def regular_tomita(grammar_index, doc_id):
#     run_tomita2(grammars[grammar_index], doc_id, 10 + grammar_index)
#     if grammar_index < grammar_count - 1:
#         regular_tomita.delay(grammar_index + 1, doc_id)
#     if grammar_index == grammar_count - 1:
#         regular_entities.delay(doc_id)
