"""main processes controller: statuses, route function and tasks"""
import logging
from urllib.error import *

import mprorp.analyzer.rubricator as rb
import mprorp.ner.feature as ner_feature
from mprorp.celery_app import app
from mprorp.crawler.site_page import find_full_text
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup
from mprorp.tomita.grammars.config import config as tomita_config
from mprorp.tomita.tomita_run import run_tomita

# from mprorp.db.dbDriver import DBSession

from mprorp.crawler.google_news import gn_start_parsing
from mprorp.crawler.yandex_news import yn_start_parsing
from mprorp.crawler.google_alerts import ga_start_parsing
from mprorp.crawler.vk import vk_start_parsing, vk_parse_item

from mprorp.analyzer.theming.themer import reg_theming

from mprorp.utils import home_dir
from mprorp.ner.NER import NER_predict
from mprorp.ner.identification import create_markup

# statuses
VK_INIT_STATUS = 10
VK_COMPLETE_STATUS = 19
GOOGLE_NEWS_INIT_STATUS = 30
GOOGLE_ALERTS_INIT_STATUS = 20
YANDEX_NEWS_INIT_STATUS = 40
#GOOGLE_NEWS_COMPLETE_STATUS = 21
SITE_PAGE_LOADING_FAILED = 91
SITE_PAGE_COMPLETE_STATUS = 99

MORPHO_COMPLETE_STATUS = 100
LEMMAS_COMPLETE_STATUS = 101
RUBRICATION_COMPLETE_STATUS = 102

TOMITA_FIRST_COMPLETE_STATUS = 200
NER_TOMITA_FEATURES_COMPLETE_STATUS = 300
NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS = 301
NER_TOMITA_MORPHO_FEATURES_COMPLETE_STATUS = 302
NER_PREDICT_COMPLETE_STATUS = 350
MARKUP_COMPLETE_STATUS = 400
THEMING_COMPLETE_STATUS = 500
NER_ENTITIES_COMPLETE_STATUS = 850
REGULAR_PROCESSES_FINISH_STATUS = 1000

VALIDATION_AND_CONVERTING_COMPLETE = 1001  # mpro redactor sets this and next status
VALIDATION_FAILED = 1002
FROM_OPEN_CORPORA = 1100
FROM_MANUAL_SOURCES_FOR_LEARNING = 1101
FOR_TRAINING = 17000
FOR_RUBRICS_TRAINING = 1200  # Normal documents from crawler that marked in redactor as for training

EMPTY_TEXT = 2000
WITHOUT_RUBRICS = 2001



rubrics_for_regular = {u'19848dd0-436a-11e6-beb8-9e71128cae02': None,
                       u'19848dd0-436a-11e6-beb8-9e71128cae21': None}   # 404f1c89-53bd-4313-842d-d4a417c88d67
grammars = list(tomita_config.keys()) #  ['date.cxx', 'person.cxx']
facts = ['Person']
ner_settings = [[home_dir + '/weights/ner_oc1.params', home_dir + '/weights/ner_oc1.weights'],
           [home_dir + '/weights/ner_oc2.params', home_dir + '/weights/ner_oc2.weights']]


def router(doc_id, status):
    """route function, that adds new tasks by incoming result (document's status)"""
    doc_id = str(doc_id)
    logging.info("route doc: " + str(doc_id) + " status: " + str(status))
    if status in [GOOGLE_NEWS_INIT_STATUS, GOOGLE_ALERTS_INIT_STATUS, YANDEX_NEWS_INIT_STATUS]:  # to find full text of HTML page
        regular_find_full_text.delay(doc_id, SITE_PAGE_COMPLETE_STATUS)
    elif status == VK_INIT_STATUS:  # to complete vk item parsing
        regular_vk_parse_item.delay(doc_id, VK_COMPLETE_STATUS)
    elif status < 100 and status%10 == 9:  # to morpho
        source_id = select([Document.source_id], Document.doc_id == doc_id).fetchone()[0]
        source_type = select([Source.source_type_id], Source.source_id == source_id).fetchone()[0]
        source_type = str(source_type)
        if source_type in ['0cc76b0c-531e-4a90-ab0b-078695336df5', '1d6210b2-5ff3-401c-b0ba-892d43e0b741', 'ce81b5dc-115c-400b-8886-91f9246926ca']:
            regular_morpho.delay(doc_id, MORPHO_COMPLETE_STATUS)
        else:  # training
            session = db_session()
            doc = session.query(Document).filter_by(doc_id=doc_id).first()
            doc.status = FOR_TRAINING
            doc.type = 'tng'
            session.commit()
            session.remove()
    elif status == MORPHO_COMPLETE_STATUS:  # to lemmas
        regular_lemmas.delay(doc_id, LEMMAS_COMPLETE_STATUS)
    elif status == LEMMAS_COMPLETE_STATUS:  # to rubrication
        regular_rubrication.delay(doc_id, RUBRICATION_COMPLETE_STATUS, WITHOUT_RUBRICS)
    elif status == RUBRICATION_COMPLETE_STATUS:  # to tomita
        regular_tomita.delay(0, doc_id, TOMITA_FIRST_COMPLETE_STATUS)
    elif status >= TOMITA_FIRST_COMPLETE_STATUS and status < TOMITA_FIRST_COMPLETE_STATUS+len(grammars)-1:  # to tomita
        regular_tomita.delay(status-TOMITA_FIRST_COMPLETE_STATUS+1, doc_id, status+1)
    elif status == TOMITA_FIRST_COMPLETE_STATUS+len(grammars)-1:  # to ner tomita
        regular_tomita_features.delay(doc_id, NER_TOMITA_FEATURES_COMPLETE_STATUS)
    elif status == NER_TOMITA_FEATURES_COMPLETE_STATUS:  # to preparing lemmas
        regular_embedding_features.delay(doc_id, NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS)
    elif status == NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS:  # to preparing morpho
        regular_morpho_features.delay(doc_id, NER_TOMITA_MORPHO_FEATURES_COMPLETE_STATUS)
    elif status == NER_TOMITA_MORPHO_FEATURES_COMPLETE_STATUS:  # to NER
        regular_NER_predict.delay(doc_id, NER_PREDICT_COMPLETE_STATUS)
    elif status == NER_PREDICT_COMPLETE_STATUS:  # to createb markup
        regular_create_markup.delay(doc_id, MARKUP_COMPLETE_STATUS)
    elif status == MARKUP_COMPLETE_STATUS:  # to ner entities
        regular_entities.delay(doc_id, NER_ENTITIES_COMPLETE_STATUS)
    elif status == NER_ENTITIES_COMPLETE_STATUS:  # fin regular processes
        session = db_session()
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        doc.status = REGULAR_PROCESSES_FINISH_STATUS
        session.commit()
        session.remove()



@app.task(ignore_result=True, time_limit=660, soft_timeout_limit=600)
def regular_gn_start_parsing(source_id):
    """parsing google news request"""
    session = db_session()
    docs = gn_start_parsing(source_id, session)
    for doc in docs:
        doc.status = GOOGLE_NEWS_INIT_STATUS
    session.commit()
    for doc in docs:
        router(doc.doc_id, GOOGLE_NEWS_INIT_STATUS)
    session.remove()


@app.task(ignore_result=True, time_limit=660, soft_timeout_limit=600)
def regular_ga_start_parsing(source_id):
    """parsing google alerts request"""
    session = db_session()
    docs = ga_start_parsing(source_id, session)
    for doc in docs:
        doc.status = GOOGLE_ALERTS_INIT_STATUS
    session.commit()
    for doc in docs:
        router(doc.doc_id, GOOGLE_ALERTS_INIT_STATUS)
    session.remove()


@app.task(ignore_result=True, time_limit=660, soft_timeout_limit=600)
def regular_yn_start_parsing(source_id):
    """parsing yandex news request"""
    session = db_session()
    docs = yn_start_parsing(source_id, session)
    for doc in docs:
        doc.status = YANDEX_NEWS_INIT_STATUS
    session.commit()
    for doc in docs:
        router(doc.doc_id, YANDEX_NEWS_INIT_STATUS)
    session.remove()


@app.task(ignore_result=True, time_limit=660, soft_timeout_limit=600)
def regular_vk_start_parsing(source_id):
    """parsing vk request"""
    session = db_session()
    docs = vk_start_parsing(source_id, session)
    for doc in docs:
        doc.status = VK_INIT_STATUS
    session.commit()
    print("regular_vk_start_parsing commit", source_id)
    for doc in docs:
        router(doc.doc_id, VK_INIT_STATUS)
    session.remove()


@app.task(ignore_result=True)
def regular_vk_parse_item(doc_id, new_status):
    """parsing vk request"""
    session, doc = get_doc(doc_id)
    vk_parse_item(doc)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_find_full_text(doc_id, new_status):
    """parsing HTML page to find full text"""
    session, doc = get_doc(doc_id)
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
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_morpho(doc_id, new_status):
    """morphologia"""
    session, doc = get_doc(doc_id)
    rb.morpho_doc(doc)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_lemmas(doc_id, new_status):
    """counting lemmas frequency for one document"""
    session, doc = get_doc(doc_id)
    rb.lemmas_freq_doc(doc)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_rubrication(doc_id, with_rubrics_status, without_rubrics_status):
    """regular rubrication"""
    session, doc = get_doc(doc_id)
    # rb.spot_doc_rubrics2(doc_id, rubrics_for_regular, new_status)
    # doc.rubric_ids = ['19848dd0-436a-11e6-beb8-9e71128cae50']
    rb.spot_doc_rubrics(doc, rubrics_for_regular, session, False)

    if len(doc.rubric_ids) == 0:
        new_status = without_rubrics_status
    else:
        new_status = with_rubrics_status
    set_doc(doc, new_status, session)

@app.task(ignore_result=True)
def regular_tomita(grammar_index, doc_id, new_status):
    """tomita"""
    session, doc = get_doc(doc_id)
    run_tomita(doc, grammars[grammar_index], session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_tomita_features(doc_id, new_status):
    """tomita features (transform coordinates for ner)"""
    session, doc = get_doc(doc_id)
    ner_feature.create_tomita_feature(doc, grammars, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_embedding_features(doc_id, new_status):
    """lemmas preparation for NER"""
    session, doc = get_doc(doc_id)
    ner_feature.create_embedding_feature(doc, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_morpho_features(doc_id, new_status):
    session, doc = get_doc(doc_id)
    ner_feature.create_morpho_feature(doc, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_NER_predict(doc_id, new_status):
    """NER computing"""
    session, doc = get_doc(doc_id)
    NER_predict(doc, ner_settings, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_create_markup(doc_id, new_status):
    """create entities if it needs and create markup"""
    session, doc = get_doc(doc_id)
    create_markup(doc, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_theming(doc_id, new_status):
    """regular theming"""
    session, doc = get_doc(doc_id)
    reg_theming(doc, session)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_entities(doc_id, new_status):
    """
    grammars_of_tomita_classes = ['loc.cxx', 'org.cxx', 'norm_act.cxx']
    convert_tomita_result_to_markup(doc, grammars_of_tomita_classes, session=session, commit_session=False)
    doc.status = new_status
    print(doc.markup)
    session.commit()
    session.remove()
    #router(doc_id, new_status)
    """
    session, doc = get_doc(doc_id)
    grammars_of_tomita_classes = ['loc.cxx', 'org.cxx', 'norm_act.cxx']
    convert_tomita_result_to_markup(doc, grammars_of_tomita_classes, session=session, commit_session=False)
    set_doc(doc, new_status, session)


def get_doc(doc_id):
    """reading doc from db"""
    session = db_session()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    return session, doc


def set_doc(doc, new_status, session):
    """writing changes to db"""
    doc.status = new_status
    session.commit()
    session.remove()
    router(doc.doc_id, new_status)

"""


@app.task(ignore_result=True)
def regular_entities(doc_id, new_status):
    grammars_of_tomita_classes = ['loc.cxx', 'org.cxx', 'norm_act.cxx']
    convert_tomita_result_to_markup(doc, grammars_of_tomita_classes, session=session, commit_session=False)
    doc.status = new_status
    print(doc.markup)
    session.commit()
    session.remove()
    #router(doc_id, new_status)

session = db_session()
doc = session.query(Document).filter_by(doc_id='3f521888-1e9f-4afd-8427-9d353cb842de').first()
print(doc.markup)
session.remove()
regular_entities('3f521888-1e9f-4afd-8427-9d353cb842de',-1)
session = db_session()
doc = session.query(Document).filter_by(doc_id='3f521888-1e9f-4afd-8427-9d353cb842de').first()
print(doc.markup)
session.remove()
"""