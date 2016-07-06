from mprorp.db.dbDriver import *
from mprorp.db.models import *

import mprorp.analyzer.rubricator as rb
from mprorp.tomita.tomita_run import run_tomita
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup
from mprorp.crawler.site_page import find_full_text
import mprorp.ner.feature as ner_feature
from mprorp.tomita.grammars.config import config as tomita_config

from mprorp.celery_app import app
import logging
from urllib.error import *

VK_COMPLETE_STATUS = 19
GOOGLE_NEWS_INIT_STATUS = 20
SITE_PAGE_LOADING_FAILED = 91
SITE_PAGE_COMPLETE_STATUS = 99
MORPHO_COMPLETE_STATUS = 100
LEMMAS_COMPLETE_STATUS = 101
RUBRICATION_COMPLETE_STATUS = 102
TOMITA_FIRST_COMPLETE_STATUS = 200
NER_TOMITA_FEATURES_COMPLETE_STATUS = 300
NER_ENTITIES_COMPLETE_STATUS = 350
REGULAR_PROCESSES_FINISH_STATUS = 1000
VALIDATION_AND_CONVERTING_COMPLETE = 1001
VALIDATION_FAILED = 1002
FROM_OPEN_CORPORA = 1100
FROM_MANUAL_SOURCES_FOR_LEARNING = 1101
EMPTY_TEXT = 2000



rubrics_for_regular = {u'76819d19-d3f7-43f1-bc7f-b10ec5a2e2cc': u'404f1c89-53bd-4313-842d-d4a417c88d67'}  # 404f1c89-53bd-4313-842d-d4a417c88d67
grammars = list(tomita_config.keys()) #  ['date.cxx', 'person.cxx']
facts = ['Person']


def router(doc_id, status):
    logging.info("route doc: " + str(doc_id) + " status: " + str(status))
    if status == GOOGLE_NEWS_INIT_STATUS:  # to find full text of HTML page
        regular_find_full_text.delay(doc_id, SITE_PAGE_COMPLETE_STATUS)
    elif status < 100 and status%10 == 9:  # to morpho
        doc_id = str(doc_id)
        regular_morpho.delay(doc_id, MORPHO_COMPLETE_STATUS)
    elif status == MORPHO_COMPLETE_STATUS:  # to lemmas
        regular_lemmas.delay(doc_id, LEMMAS_COMPLETE_STATUS)
    elif status == LEMMAS_COMPLETE_STATUS:  # to rubrication
        regular_rubrication.delay(doc_id, RUBRICATION_COMPLETE_STATUS)
    elif status == RUBRICATION_COMPLETE_STATUS:  # to tomita
        regular_tomita.delay(0, doc_id, TOMITA_FIRST_COMPLETE_STATUS)
    elif status >= TOMITA_FIRST_COMPLETE_STATUS and status < TOMITA_FIRST_COMPLETE_STATUS+len(grammars)-1:  # to tomita
        regular_tomita.delay(status-TOMITA_FIRST_COMPLETE_STATUS+1, doc_id, status+1)
    elif status == TOMITA_FIRST_COMPLETE_STATUS+len(grammars)-1:  # to ner tomita
        regular_tomita_features.delay(doc_id, NER_TOMITA_FEATURES_COMPLETE_STATUS)
    elif status == NER_TOMITA_FEATURES_COMPLETE_STATUS:  # to ner entities
        regular_entities.delay(doc_id, NER_ENTITIES_COMPLETE_STATUS)
    elif status == NER_ENTITIES_COMPLETE_STATUS:  # fin regular processes
        doc = Document(doc_id = doc_id, status = REGULAR_PROCESSES_FINISH_STATUS)
        update(doc)


# parsing HTML page to find full text
@app.task
def regular_find_full_text(doc_id, new_status):
    try:
        find_full_text(doc_id, new_status, SITE_PAGE_LOADING_FAILED)
        router(doc_id, new_status)
    except Exception as err:
        err_txt = repr(err)
        if err_txt == 'Empty text':
            logging.error("Пустой текст doc_id: " + doc_id)
            err_status = EMPTY_TEXT
        elif type(err) == HTTPError:
            # print(url, err.code)
            err_status = SITE_PAGE_LOADING_FAILED
            logging.error("Ошибка загрузки код: " + str(err.code) + " doc_id: " + doc_id) # + " url: " + url)
        else:
            # print(url, type(err))
            err_status = SITE_PAGE_LOADING_FAILED
            logging.error("Неизвестная ошибка doc_id: " + doc_id)

        doc = Document(doc_id=doc_id, status=err_status)
        update(doc)
        router(doc_id, err_status)




# morphologia
@app.task
def regular_morpho(doc_id, new_status):
    rb.morpho_doc(doc_id, new_status)
    router(doc_id, new_status)


# counting lemmas frequency for one document
@app.task
def regular_lemmas(doc_id, new_status):
    rb.lemmas_freq_doc(doc_id, new_status)
    router(doc_id, new_status)


# regular rubrication
@app.task
def regular_rubrication(doc_id, new_status):
    rb.spot_doc_rubrics(doc_id, rubrics_for_regular, new_status)
    router(doc_id, new_status)


# tomita
@app.task
def regular_tomita(grammar_index, doc_id, new_status):
    run_tomita(grammars[grammar_index], doc_id, new_status)
    router(doc_id, new_status)


# tomita features
@app.task
def regular_tomita_features(doc_id, new_status):
    ner_feature.create_tomita_feature(doc_id, grammars, new_status)
    router(doc_id, new_status)


# ner entities
@app.task
def regular_entities(doc_id, new_status):
    convert_tomita_result_to_markup(doc_id, grammars, new_status=new_status)
    router(doc_id, new_status)