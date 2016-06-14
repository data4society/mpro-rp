from mprorp.tomita_grammars.test_tomita.tomita_start import start_tomita
from mprorp.tomita_grammars.test_tomita.tomita_out import tomita_out

def run_tomita(grammar, doc_id):
    output = start_tomita(grammar, doc_id)
    out = tomita_out(output)
    return out

run_tomita('date.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6')