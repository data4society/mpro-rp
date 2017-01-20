from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.tomita.tomita_run import run_tomita2

for gram in grammar_config:
    run_tomita2(gram, 'c8236b7e-b0a3-43c1-8601-cb57a055189d')

