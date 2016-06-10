from mprorp.tomita_grammars.test_tomita.tomita_start import start_tomita
from mprorp.tomita_grammars.test_tomita.tomita_out import tomita_out

def run_tomita(grammar, doc_id):
    output = start_tomita(grammar, doc_id)
    tomita_out(output)
