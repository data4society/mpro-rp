"""function to run tomita and extract facts coordinates"""
import os

import mprorp.analyzer.db as db
from mprorp.tomita.tomita_out import tomita_out, norm_out, find_act
from mprorp.tomita.tomita_start import start_tomita, create_file
from mprorp.tomita.tomita_run_ovd import run_tomita_ovd


def del_files(doc_id):
    """function to delete temporal files"""
    file_name1 = doc_id + '.txt'
    file_name2 = 'config_' + doc_id + '.proto'
    file_name3 = 'facts_' + doc_id + '.txt'
    os.remove(file_name1, dir_fd=None)
    os.remove(file_name2, dir_fd=None)
    os.remove(file_name3, dir_fd=None)


def run_tomita2(grammar, doc_id, status=0):
    return db.doc_apply(doc_id, run_tomita, grammar)


def run_tomita(doc, grammar, session=None, commit_session=True):
    """the final function to run tomita_start and tomita_run together"""
    if grammar == 'norm_act.cxx':
        source_name = create_file(doc)
        out = norm_out(find_act(source_name), source_name)
        db.put_tomita_result(str(doc.doc_id), grammar, out, session, commit_session)
        file_name1 = str(doc.doc_id) + '.txt'
        os.remove(file_name1, dir_fd=None)
        return out
    elif grammar == 'ovd.cxx':
        out = run_tomita_ovd(doc, n=1)
        db.put_tomita_result(str(doc.doc_id), grammar, out, session, commit_session)
        return out
    else:
        output = start_tomita(grammar, doc)
        source_name = str(doc.doc_id) + '.txt'
        out = tomita_out(output, source_name)
        db.put_tomita_result(str(doc.doc_id), grammar, out, session, commit_session)
        del_files(str(doc.doc_id))
        return out


#start_tomita('date.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6')
#print(run_tomita2('date.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6', status=0))
#print(run_tomita2('person.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6', status=0))
#print(run_tomita2('loc.cxx', '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6', status=0))
#print(run_tomita2('date.cxx', '75fa182d-7fbc-4ec7-bbfd-fc4d743e8834', status=0))