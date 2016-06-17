from mprorp.tomita.tomita_run import run_tomita

grammars = ['date.cxx', 'person.cxx']
grammar_count = 2


def regular_tomita(grammar_index, doc_id):
    run_tomita(grammars[grammar_index], doc_id, 10 + grammar_index)
