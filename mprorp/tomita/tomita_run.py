import os

from mprorp.analyzer.db import put_tomita_result
from mprorp.tomita.tomita_out import tomita_out
from mprorp.tomita.tomita_start import start_tomita


def del_files(doc_id):
    file_name1 = doc_id + '.txt'
    file_name2 = 'config_' + doc_id + '.proto'
    file_name3 = 'facts_' + doc_id + '.txt'
    os.remove(file_name1, dir_fd=None)
    os.remove(file_name2, dir_fd=None)
    os.remove(file_name3, dir_fd=None)


def run_tomita(grammar, doc_id, status=0):
    output = start_tomita(grammar, doc_id)
    out = tomita_out(output)
    put_tomita_result(doc_id, grammar, out, status)
    del_files(doc_id)
    return out

# start_tomita('date.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6')
# print(run_tomita('date.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'))
# print(run_tomita('person.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'))