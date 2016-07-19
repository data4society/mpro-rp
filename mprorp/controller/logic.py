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

from mprorp.db.dbDriver import DBSession

from mprorp.crawler.google_news import gn_start_parsing
from mprorp.crawler.vk import vk_start_parsing

VK_COMPLETE_STATUS = 19
GOOGLE_NEWS_INIT_STATUS = 20
GOOGLE_NEWS_INIT_STATUS = 21
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
FOR_TRAINING = 1000
EMPTY_TEXT = 2000



rubrics_for_regular = {u'76819d19-d3f7-43f1-bc7f-b10ec5a2e2cc': u'404f1c89-53bd-4313-842d-d4a417c88d67'}  # 404f1c89-53bd-4313-842d-d4a417c88d67
grammars = list(tomita_config.keys()) #  ['date.cxx', 'person.cxx']
facts = ['Person']


def router(doc_id, status):
    doc_id = str(doc_id)
    logging.info("route doc: " + str(doc_id) + " status: " + str(status))
    if status == GOOGLE_NEWS_INIT_STATUS:  # to find full text of HTML page
        regular_find_full_text.delay(doc_id, SITE_PAGE_COMPLETE_STATUS)
    elif status < 100 and status%10 == 9:  # to morpho
        source_id = select([Document.source_id], Document.doc_id == doc_id).fetchone()[0]
        source_type = select([Source.source_type_id], Source.source_id == source_id).fetchone()[0]
        source_type = str(source_type)
        if source_type in ['0cc76b0c-531e-4a90-ab0b-078695336df5','1d6210b2-5ff3-401c-b0ba-892d43e0b741']:
            #doc_id = str(doc_id)
            regular_morpho.delay(doc_id, MORPHO_COMPLETE_STATUS)
        else:
            doc = Document(doc_id=doc_id, status=FOR_TRAINING, type='tng')
            update(doc)
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


# parsing google news request
@app.task(ignore_result=True)
def regular_gn_start_parsing(source_id):
    session = DBSession()
    docs = gn_start_parsing(source_id, session)
    for doc in docs:
        doc.status = GOOGLE_NEWS_INIT_STATUS
    session.commit()
    for doc in docs:
        router(doc.doc_id, GOOGLE_NEWS_INIT_STATUS)
    session.close()

# parsing vk request
@app.task(ignore_result=True)
def regular_vk_start_parsing(source_id):
    session = DBSession()
    docs = vk_start_parsing(source_id, session)
    for doc in docs:
        doc.status = VK_COMPLETE_STATUS
    session.commit()
    for doc in docs:
        router(doc.doc_id, VK_COMPLETE_STATUS)
    session.close()


# parsing HTML page to find full text
@app.task(ignore_result=True)
def regular_find_full_text(doc_id, new_status):
    session = DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    try:
        find_full_text(doc)
    except Exception as err:
        err_txt = repr(err)
        if err_txt == 'Empty text':
            logging.error("Пустой текст doc_id: " + doc_id)
            new_status = EMPTY_TEXT
        elif type(err) == HTTPError:
            # print(url, err.code)
            new_status = SITE_PAGE_LOADING_FAILED
            logging.error("Ошибка загрузки код: " + str(err.code) + " doc_id: " + doc_id) # + " url: " + url)
        else:
            # print(url, type(err))
            new_status = SITE_PAGE_LOADING_FAILED
            logging.error("Неизвестная ошибка doc_id: " + doc_id)

    doc.status = new_status
    session.commit()
    session.close()
    router(doc_id, new_status)


# morphologia
@app.task(ignore_result=True)
def regular_morpho(doc_id, new_status):
    session = DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    rb.morpho_doc(doc)
    doc.status = new_status
    session.commit()
    session.close()
    router(doc_id, new_status)


# counting lemmas frequency for one document
@app.task(ignore_result=True)
def regular_lemmas(doc_id, new_status):
    session = DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    rb.lemmas_freq_doc(doc)
    doc.status = new_status
    session.commit()
    session.close()
    router(doc_id, new_status)


# regular rubrication
@app.task(ignore_result=True)
def regular_rubrication(doc_id, new_status):
    session = DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    # rb.spot_doc_rubrics2(doc_id, rubrics_for_regular, new_status)
    doc.rubric_ids = ['19848dd0-436a-11e6-beb8-9e71128cae50']
    doc.status = new_status
    session.commit()
    session.close()
    router(doc_id, new_status)


# tomita
@app.task(ignore_result=True)
def regular_tomita(grammar_index, doc_id, new_status):
    session = DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    run_tomita(doc, grammars[grammar_index], session, False)
    doc.status = new_status
    session.commit()
    session.close()
    router(doc_id, new_status)


# tomita features
@app.task(ignore_result=True)
def regular_tomita_features(doc_id, new_status):
    session = DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    ner_feature.create_tomita_feature(doc, grammars, session, False)
    doc.status = new_status
    session.commit()
    session.close()
    router(doc_id, new_status)


# ner entities
@app.task(ignore_result=True)
def regular_entities(doc_id, new_status):
    session = DBSession()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    convert_tomita_result_to_markup(doc, grammars, session=session, commit_session=False)
    doc.status = new_status
    session.commit()
    session.close()
    router(doc_id, new_status)