import csv
from mprorp.db.dbDriver import db_session
from mprorp.db.models import *
from sqlalchemy.orm import load_only
from mprorp.analyzer.theming.themer import THEME_THRESHOLD, WORD_GOOD_THRESHOLD, WORD_MIN_MENTIONS, MAX_THEME_PAUSE, MAIN_WORDS_FROM_TEXT_LENGTH, THEMING_SOURCE, THEMING_GEOMETRIA
import os


def get_estimate():
    experts = dict()
    systems = dict()
    expert_themes = []
    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'/corpus/corpus.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            expert_theme = row[3]
            experts[row[0]] = expert_theme
            if expert_theme not in expert_themes:
                expert_themes.append(expert_theme)
    keys = list(experts.keys())
    print("Число экспертных сюжетов:",len(expert_themes))
    themes = []
    session = db_session()
    docs = session.query(Document).options(load_only("doc_id","theme_id")).\
        filter(Document.doc_id.in_(keys)).\
        order_by(Document.created).all()
    for doc in docs:
        theme_id = str(doc.theme_id)
        systems[str(doc.doc_id)] = theme_id
        if theme_id not in themes:
            themes.append(theme_id)
    print("Число машинных сюжетов:",len(themes))
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
    print("THEMING_SOURCE:",THEMING_SOURCE)
    print("THEMING_GEOMETRIA:",THEMING_GEOMETRIA)
    print("THEME_THRESHOLD:",THEME_THRESHOLD)
    print("WORD_MIN_MENTIONS:",WORD_MIN_MENTIONS)
    print("WORD_GOOD_THRESHOLD:",WORD_GOOD_THRESHOLD)
    print("MAX_THEME_PAUSE:",MAX_THEME_PAUSE)
    print("MAIN_WORDS_FROM_TEXT_LENGTH:",MAIN_WORDS_FROM_TEXT_LENGTH)
    print("TP:",tp)
    print("FP:",fp)
    print("FN:",fn)
    print("TN:",tn)
    print("Precision:",tp/(tp+fp))
    print("Recall:",tp/(tp+fn))


if __name__ == '__main__':
    """start testing from here"""
    get_estimate()


