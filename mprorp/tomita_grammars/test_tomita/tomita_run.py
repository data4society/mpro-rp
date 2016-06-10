from mprorp.tomita_grammars.test_tomita.tomita_start import start_tomita
from mprorp.tomita_grammars.test_tomita.tomita_out import tomita_out

def run_tomita(grammar, file_name):
    output = start_tomita(grammar, file_name)
    tomita_out(output)
