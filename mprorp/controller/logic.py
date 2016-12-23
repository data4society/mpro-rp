"""main processes controller: statuses, route function and tasks"""
import logging
from urllib.error import *

import mprorp.analyzer.rubricator as rb
import mprorp.ner.feature as ner_feature
from mprorp.celery_app import app
from mprorp.crawler.site_page import find_full_text
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from sqlalchemy.orm.attributes import flag_modified
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup
from mprorp.tomita.tomita_run import run_tomita

# from mprorp.db.dbDriver import DBSession

from mprorp.crawler.google_news import gn_start_parsing
from mprorp.crawler.yandex_news import yn_start_parsing
from mprorp.crawler.google_alerts import ga_start_parsing
from mprorp.crawler.vk import vk_start_parsing, vk_parse_item
from mprorp.crawler.csv_to_rubricator import csv_start_parsing
from mprorp.crawler.from_other_app import other_app_cloning

from mprorp.analyzer.theming.themer import regular_themization

from mprorp.utils import home_dir, relative_file_path
from mprorp.ner.NER import NER_predict
from mprorp.ner.identification import create_markup_regular
from mprorp.analyzer.rubrication_by_comparing import reg_rubrication_by_comparing

import json
import datetime

# statuses
VK_INIT_STATUS = 10
VK_COMPLETE_STATUS = 19
GOOGLE_NEWS_INIT_STATUS = 30
GOOGLE_ALERTS_INIT_STATUS = 20
YANDEX_NEWS_INIT_STATUS = 40
CSV_INIT_STATUS = 50
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
RUBRICATION_BY_COMPARING_COMPLETE_STATUS = 950
REGULAR_PROCESSES_FINISH_STATUS = 1000

VALIDATION_AND_CONVERTING_COMPLETE = 1001  # mpro redactor sets this and next status
VALIDATION_FAILED = 1002
FROM_OPEN_CORPORA = 1100
FROM_MANUAL_SOURCES_FOR_LEARNING = 1101
FOR_TRAINING = 1000
FOR_RUBRICS_TRAINING = 1200  # Normal documents from crawler that marked in redactor as for training

EMPTY_TEXT = 2000
SHORT_LENGTH = 2002
WITHOUT_RUBRICS = 2001


def router(doc_id, app_id, status):
    """route function, that adds new tasks by incoming result (document's status)"""
    doc_id = str(doc_id)
    apps_config = variable_get("last_config")
    app_conf = apps_config[app_id]
    logging.info("route doc: " + str(doc_id) + " status: " + str(status) + " app_id: " + app_id)
    if status in [SITE_PAGE_LOADING_FAILED, EMPTY_TEXT]:
        return
    if status in [GOOGLE_NEWS_INIT_STATUS, GOOGLE_ALERTS_INIT_STATUS, YANDEX_NEWS_INIT_STATUS, CSV_INIT_STATUS]:  # to find full text of HTML page
        regular_find_full_text.delay(doc_id, SITE_PAGE_COMPLETE_STATUS, app_id=app_id)
        return
    if status == VK_INIT_STATUS:  # to complete vk item parsing
        regular_vk_parse_item.delay(doc_id, VK_COMPLETE_STATUS, app_id=app_id)
        return
    if "min_length_validation" in app_conf:
        session = db_session()
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        if len(doc.stripped) < app_conf["min_length_validation"]:
            status = SHORT_LENGTH
            doc.status = status
            session.commit()
            session.remove()
            return status
        session.remove()
    if "force_rubrication" in app_conf:
        session = db_session()
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        doc.rubric_ids = app_conf["force_rubrication"]
        session.commit()
        session.remove()
    if "force_url_doomain" in app_conf:
        session = db_session()
        record_id = str(
            session.query(Record).filter_by(source=doc_id).options(load_only("document_id")).first().document_id)
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        doc.url = app_conf["force_url_doomain"] + '/#page=inbox,documentId=' + record_id + ',app=' + doc.source_with_type.split(" ")[1]
        session.commit()
        session.remove()
    if status < MORPHO_COMPLETE_STATUS and "morpho" in app_conf:  # to morpho
        regular_morpho.delay(doc_id, MORPHO_COMPLETE_STATUS, app_id=app_id)
        return
    if status < LEMMAS_COMPLETE_STATUS and "lemmas" in app_conf:  # to lemmas
        regular_lemmas.delay(doc_id, LEMMAS_COMPLETE_STATUS, app_id=app_id)
        return
    if status < RUBRICATION_COMPLETE_STATUS and "rubrication" in app_conf:  # to rubrication
        regular_rubrication.delay(app_conf["rubrication"], doc_id, RUBRICATION_COMPLETE_STATUS, WITHOUT_RUBRICS, app_id=app_id)
        return
    if "tomita" in app_conf:
        grammars = list(app_conf["tomita"]["grammars"].keys())  # ['date.cxx', 'person.cxx']
        if status < TOMITA_FIRST_COMPLETE_STATUS+len(grammars)-1:  # to tomita
            if status < TOMITA_FIRST_COMPLETE_STATUS:
                regular_tomita.delay(grammars[0], doc_id, TOMITA_FIRST_COMPLETE_STATUS, app_id=app_id)
            else:
                regular_tomita.delay(grammars[status - TOMITA_FIRST_COMPLETE_STATUS + 1], doc_id, status + 1, app_id=app_id)
            return
        if "tomita_features" in app_conf["tomita"] and status < NER_TOMITA_FEATURES_COMPLETE_STATUS:  # to ner tomita
            regular_tomita_features.delay(grammars, doc_id, NER_TOMITA_FEATURES_COMPLETE_STATUS, app_id=app_id)
            return
    if "ner_tomita_embedding_features" in app_conf and status < NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS:  # to preparing lemmas
        regular_embedding_features.delay(doc_id, NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS, app_id=app_id)
        return
    if "ner_tomita_morpho_features" in app_conf and status < NER_TOMITA_MORPHO_FEATURES_COMPLETE_STATUS:  # to preparing morpho
        regular_morpho_features.delay(doc_id, NER_TOMITA_MORPHO_FEATURES_COMPLETE_STATUS, app_id=app_id)
        return
    if "ner_predict" in app_conf and status < NER_PREDICT_COMPLETE_STATUS:  # to NER
        regular_NER_predict.delay(app_conf["ner_predict"]["ner_settings"], doc_id, NER_PREDICT_COMPLETE_STATUS, app_id=app_id)
        return
    if "markup" in app_conf and status < MARKUP_COMPLETE_STATUS:  # to create markup
        regular_create_markup.delay(app_conf["markup"], doc_id, MARKUP_COMPLETE_STATUS, app_id=app_id)
        return
    if "theming" in app_conf and status < THEMING_COMPLETE_STATUS:  # to set theme
        regular_theming.delay(doc_id, THEMING_COMPLETE_STATUS, app_id=app_id)
        return
    if "tomita_entities" in app_conf and status < NER_ENTITIES_COMPLETE_STATUS:  # to ner entities
        tomita_entities.delay(app_conf["tomita_entities"], doc_id, NER_ENTITIES_COMPLETE_STATUS, app_id=app_id)
        return
    if "rubrication_by_comparing" in app_conf and status < RUBRICATION_BY_COMPARING_COMPLETE_STATUS:  # to set theme
        regular_rubrication_by_comparing.delay(app_conf["rubrication_by_comparing"], doc_id, RUBRICATION_BY_COMPARING_COMPLETE_STATUS, app_id=app_id)
        return

    # finish regular procedures:
    session = db_session()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    if "special_type" in app_conf:
        doc.type = app_conf["special_type"]
    if "special_final_status" in app_conf:
        status = app_conf["special_final_status"]
    else:
        status = REGULAR_PROCESSES_FINISH_STATUS
    doc.status = status
    session.commit()
    session.remove()
    return status


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_gn_start_parsing(source_key, **kwargs):
    """parsing google news request"""
    print("GN CRAWL START: "+source_key)
    session = db_session()
    apps_config = variable_get("last_config",session)
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["google_news"][source_key]
    blacklist = apps_config[app_id]["blacklist"] if "blacklist" in apps_config[app_id] else []
    try:
        docs = gn_start_parsing(source_key, blacklist, app_id, session)
        for doc in docs:
            doc.status = GOOGLE_NEWS_INIT_STATUS
            doc.source_with_type = "google_news "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id,  GOOGLE_NEWS_INIT_STATUS)
    except Exception as err:
        err_txt = repr(err)
        logging.error("Неизвестная ошибка google_news краулера, source: " + source_key)
        print(err_txt)
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='google_news', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("GN CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_ga_start_parsing(source_key, **kwargs):
    """parsing google alerts request"""
    print("GA CRAWL START: "+source_key)
    session = db_session()
    apps_config = variable_get("last_config",session)
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["google_alerts"][source_key]
    blacklist = apps_config[app_id]["blacklist"] if "blacklist" in apps_config[app_id] else []
    try:
        docs = ga_start_parsing(source_key, blacklist, app_id, session)
        for doc in docs:
            doc.status = GOOGLE_ALERTS_INIT_STATUS
            doc.source_with_type = "google_alerts "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id, GOOGLE_ALERTS_INIT_STATUS)
    except Exception as err:
        err_txt = repr(err)
        logging.error("Неизвестная ошибка google_alerts краулера, source: " + source_key)
        print(err_txt)
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='google_alerts', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("GA CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_yn_start_parsing(source_key, **kwargs):
    """parsing yandex news request"""
    print("YN CRAWL START: "+source_key)
    session = db_session()
    apps_config = variable_get("last_config", session)
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["yandex_news"][source_key]
    blacklist = apps_config[app_id]["blacklist"] if "blacklist" in apps_config[app_id] else []
    try:
        docs = yn_start_parsing(source_key, blacklist, source["pass"], app_id, session)
        for doc in docs:
            doc.status = YANDEX_NEWS_INIT_STATUS
            doc.source_with_type = "yandex_news "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id, YANDEX_NEWS_INIT_STATUS)
    except Exception as err:
        err_txt = repr(err)
        logging.error("Неизвестная ошибка yandex_news краулера, source: " + source_key)
        print(err_txt)
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='yandex_news', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("YN CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_csv_start_parsing(source_key, **kwargs):
    """parsing csv"""
    print("CSV CRAWL START: "+source_key)
    session = db_session()
    apps_config = variable_get("last_config",session)
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["csv_to_rubricator"][source_key]
    blacklist = apps_config[app_id]["blacklist"] if "blacklist" in apps_config[app_id] else []
    try:
        docs = csv_start_parsing(source_key, blacklist, app_id, session)
        for doc in docs:
            doc.status = CSV_INIT_STATUS
            doc.source_with_type = "csv "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id, CSV_INIT_STATUS)
    except Exception as err:
        err_txt = repr(err)
        logging.error("Неизвестная ошибка csv краулера, source: " + source_key)
        print(err_txt)
    session.remove()
    print("CSV CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_other_app_start_parsing(source_key, **kwargs):
    """cloning docs from other app"""
    print("OA CRAWL START: "+source_key)
    session = db_session()
    apps_config = variable_get("last_config", session)
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["other_app"][source_key]
    blacklist = apps_config[app_id]["blacklist"] if "blacklist" in apps_config[app_id] else []
    try:
        docs = other_app_cloning(source_key, blacklist, source["url_domain"], source["fields_to_clone"], source["source_status"], app_id, session)
        for doc in docs:
            doc.status = source["start_status"]
            doc.source_with_type = "other_app "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id, source["start_status"])
    except Exception as err:
        err_txt = repr(err)
        logging.error("Неизвестная ошибка other_app краулера, source: " + source_key)
        print(err_txt)
    session.remove()
    print("OA CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_vk_start_parsing(source_key, **kwargs):
    """parsing vk request"""
    print("VK CRAWL START: "+source_key)
    session = db_session()
    apps_config = variable_get("last_config",session)
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["vk"][source_key]
    try:
        docs = vk_start_parsing(source_key, app_id, session)
        for doc in docs:
            doc.status = VK_INIT_STATUS
            doc.source_with_type = "vk "+source_key
            doc.app_id = app_id
        session.commit()
        print("regular_vk_start_parsing commit", source_key)
        for doc in docs:
            router(doc.doc_id, doc.app_id, VK_INIT_STATUS)
    except Exception as err:
        err_txt = repr(err)
        logging.error("Неизвестная ошибка vk краулера, source: " + source_key)
        print(err_txt)
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='yandex_news', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("VK CRAWL COMPLETE: "+source_key)


#@app.task(ignore_result=True)
@app.task()
def regular_vk_parse_item(doc_id, new_status, **kwargs):
    """parsing vk request"""
    session, doc = get_doc(doc_id)
    vk_parse_item(doc)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_find_full_text(doc_id, new_status, **kwargs):
    """parsing HTML page to find full text"""
    session, doc = get_doc(doc_id)
    try:
        find_full_text(doc)
        flag_modified(doc, "meta")
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
            logging.error("Неизвестная ошибка загрузки doc_id: " + doc_id + "url:" + doc.url)
        print(err_txt)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_morpho(doc_id, new_status, **kwargs):
    """morphologia"""
    session, doc = get_doc(doc_id)
    rb.morpho_doc(doc)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_lemmas(doc_id, new_status, **kwargs):
    """counting lemmas frequency for one document"""
    session, doc = get_doc(doc_id)
    rb.lemmas_freq_doc(doc)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_rubrication(rubrics, doc_id, with_rubrics_status, without_rubrics_status, **kwargs):
    """regular rubrication"""
    session, doc = get_doc(doc_id)
    # rb.spot_doc_rubrics2(doc_id, rubrics_for_regular, new_status)
    # doc.rubric_ids = ['19848dd0-436a-11e6-beb8-9e71128cae50']
    rb.spot_doc_rubrics(doc, rubrics, session, False)

    if len(doc.rubric_ids) == 0:
        new_status = without_rubrics_status
    else:
        new_status = with_rubrics_status
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_tomita(grammar, doc_id, new_status, **kwargs):
    """tomita"""
    session, doc = get_doc(doc_id)
    run_tomita(doc, grammar, session, False)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_tomita_features(grammars, doc_id, new_status, **kwargs):
    """tomita features (transform coordinates for ner)"""
    session, doc = get_doc(doc_id)
    ner_feature.create_tomita_feature(doc, grammars, session, False)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_embedding_features(doc_id, new_status, **kwargs):
    """lemmas preparation for NER"""
    session, doc = get_doc(doc_id)
    ner_feature.create_embedding_feature(doc, session, False)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_morpho_features(doc_id, new_status, **kwargs):
    session, doc = get_doc(doc_id)
    ner_feature.create_morpho_feature(doc, session, False)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task(time_limit=190, soft_time_limit=180)
def regular_NER_predict(ner_settings, doc_id, new_status, **kwargs):
    """NER computing"""
    session, doc = get_doc(doc_id)
    NER_predict(doc, ner_settings, session, False)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_create_markup(markup_settings, doc_id, new_status, **kwargs):
    """create entities if it needs and create markup"""
    session, doc = get_doc(doc_id)
    # create_markup(doc, session, False)
    create_markup_regular(doc, markup_settings, session, False)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def regular_theming(doc_id, new_status, **kwargs):
    """regular theming"""
    session, doc = get_doc(doc_id)
    regular_themization(doc, session)
    return set_doc(doc, new_status, session)


#@app.task(ignore_result=True)
@app.task()
def tomita_entities(grammars_of_tomita_classes, doc_id, new_status, **kwargs):
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
    #grammars_of_tomita_classes = ['loc.cxx', 'org.cxx', 'norm_act.cxx']
    convert_tomita_result_to_markup(doc, grammars_of_tomita_classes, session=session, commit_session=False)
    return set_doc(doc, new_status, session)



#@app.task(ignore_result=True)
@app.task()
def regular_rubrication_by_comparing(config, doc_id, new_status, **kwargs):
    """rubrication by comparing with clone source"""
    session, doc = get_doc(doc_id)
    reg_rubrication_by_comparing(doc, config, session)
    return set_doc(doc, new_status, session)


def get_doc(doc_id):
    """reading doc from db"""
    session = db_session()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    return session, doc


def set_doc(doc, new_status, session):
    """writing changes to db"""
    doc.status = new_status
    session.commit()
    doc_id = doc.doc_id
    session.remove()
    return router(doc_id, doc.app_id, new_status) or new_status



"""

regular_find_full_text('7b6428ea-435f-4a40-bdc1-19ffb3f3097a', 7000)

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

if __name__ == '__main__':
    print("LOGIC START")
    print("LOGIC FIN")