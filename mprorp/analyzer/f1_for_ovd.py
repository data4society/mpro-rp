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
    session = db_session()
    tests = session.query(Record).filter(Record.app_id == 'ovd_test').all()
    ideals = session.query(Record).filter(Record.app_id == 'ovd_ideal').all()
    for test in tests:
        ideal_id = re.findall('documentId=(.*?),app=ovd_ideal', test.url)[0]
        for ideal in ideals:
            if str(ideal.document_id) == ideal_id:
                a, b, c = prf(test.entities, ideal.entities)
                tp += a
                fp += b
                fn += c
    presicion = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * presicion * recall / (presicion + recall)
    return presicion, recall, f1