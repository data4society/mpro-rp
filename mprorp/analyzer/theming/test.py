import mprorp.crawler.readability.readability_kingwkb as kingwkb
import csv
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from sqlalchemy.orm import load_only


def get_estimate():
    experts = dict()
    systems = dict()
    with open('corpus/corpus.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            experts[row[0]] = row[3]
    print(experts)
    keys = list(experts.keys())
    print(keys)
    session = db_session()
    docs = session.query(Document).options(load_only("doc_id","theme_id")).\
        filter(Document.doc_id.in_(keys)).\
        order_by(Document.created).all()
    for doc in docs:
        systems[str(doc.doc_id)] = doc.theme_id
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    for doc_id in systems:
        for doc_id1 in systems:
            experts_estimate = experts[doc_id] == experts[doc_id1]
            systems_estimate = systems[doc_id] == systems[doc_id1]
            if experts_estimate:
                if systems_estimate:
                    tp += 1
                else:
                    fn += 1
            else:
                if systems_estimate:
                    fp += 1
                else:
                    tn += 1
    print("Размер корпуса:",len(docs))
    print("TP:",tp)
    print("FP:",fp)
    print("FN:",fn)
    print("TN:",tn)
    print("Precision:",tp/(tp+fp))
    print("Recall:",tp/(tp+fn))


if __name__ == '__main__':
    """start testing from here"""
    get_estimate()


