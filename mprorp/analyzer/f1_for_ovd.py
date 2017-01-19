from mprorp.analyzer.db import *
from mprorp.db.models import *
import re

def prf(tomita_result, original):
    tp = 0
    fp = 0
    fn = 0
    tomita = list(set([i for i in tomita_result]))
    org = list(set([i for i in original]))
    for ovd in tomita:
        if ovd in org:
            tp += 1
        else:
            fp += 1
    for ovd in org:
        if ovd not in tomita:
            fn += 1
    return tp, fp, fn

def f1():
    tp = 0
    fp = 0
    fn = 0
    null = 0
    null_F =0
    full = 0
    full_F = 0
    session = db_session()
    tests = session.query(Record).filter(Record.app_id == 'ovd_test').all()
    print('documents: ' + str(len(tests)))
    ideals = session.query(Record).filter(Record.app_id == 'ovd_ideal').all()
    for test in tests:
        ideal_id = re.findall('documentId=(.*?),app=ovd_ideal', test.url)[0]
        for ideal in ideals:
            if str(ideal.document_id) == ideal_id:
                a, b, c = prf(test.entities, ideal.entities)
                tp += a
                fp += b
                fn += c
                if ideal.entities == ():
                    null += 1
                    if b != 0:
                        null_F += 1
                else:
                    full += 1
                    if b != 0 or c != 0:
                        full_F += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    print('precision ', precision)
    print('recall ', recall)
    print('f1 ', f1)
    print('documents_len ', len(tests))
    print('empty ', null)
    print('full ', full)
    print('bad empty ', null_F)
    print('bad full ', full_F)