"""main processes controller: statuses, route function and tasks"""
import sys
import traceback
import logging

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', filename = u'/home/mprorp/mpro-rp-dev/cel.txt')
root = logging.getLogger()
root.setLevel(logging.DEBUG)
logging.info(sys.argv)
try:
    from mprorp.controller.init import *
    if worker == "main":
        from mprorp.crawler.google_news import gn_start_parsing
        from mprorp.crawler.yandex_rss import ya_rss_start_parsing
        from mprorp.crawler.yandex_news import yn_start_parsing
        from mprorp.crawler.google_alerts import ga_start_parsing
        from mprorp.crawler.vk import vk_start_parsing, vk_parse_item
        from mprorp.crawler.csv_to_rubricator import csv_start_parsing
        from mprorp.crawler.from_csv import from_csv_start_parsing
        from mprorp.crawler.from_other_app import other_app_cloning
        from mprorp.crawler.selector import selector_start_parsing
        from mprorp.crawler.refactor import refactor_start_parsing
        from mprorp.crawler.rss import rss_start_parsing
        from mprorp.crawler.central import central_start_parsing
    elif worker == "default":
        from mprorp.crawler.site_page import find_full_text
        import mprorp.analyzer.rubricator as rb
        import mprorp.ner.feature as ner_feature
        from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup
        from mprorp.tomita.tomita_run import run_tomita
        from mprorp.ner.feature import create_capital_feature
        from mprorp.ner.NER import NER_predict
        from mprorp.ner.identification import create_markup_regular
        from mprorp.analyzer.rubrication_by_comparing import reg_rubrication_by_comparing
        from mprorp.ner.paragraph_embedding import calc_paragraph_embedding
    elif worker == "fastart":
        from mprorp.analyzer.fasttext_rubrication import reg_fasttext_embedding
    elif worker == "network":
        from urllib.error import *
        from mprorp.crawler.downloader import download_page
        from mprorp.crawler.rss import one_rss_parsing
    elif worker == "theme":
        from mprorp.analyzer.theming.themer import regular_themization
    if flask_instance:
        from mprorp.central_app import app
    else:
        from mprorp.celery_app import app
    from mprorp.db.dbDriver import *
    from mprorp.db.models import *
    from sqlalchemy.orm.attributes import flag_modified
    from mprorp.utils import print_exception
    import datetime
    import inspect
except Exception as err:
    logging.info(sys.argv)
    err_txt = traceback.format_exc()
    logging.info(err_txt)


# statuses
VK_INIT_STATUS = 10
VK_COMPLETE_STATUS = 19
GOOGLE_NEWS_INIT_STATUS = 30
GOOGLE_ALERTS_INIT_STATUS = 20
YANDEX_NEWS_INIT_STATUS = 40
CSV_INIT_STATUS = 50
YANDEX_RSS_INIT_STATUS = 60
RSS_INIT_STATUS = 65
SELECTOR_INIT_STATUS = 70
FROM_CSV_INIT_STATUS = 80
SITE_PAGE_LOADING_COMPLETE_STATUS = 95
SITE_PAGE_READABILITY_COMPLETE_STATUS = 99

#OLD_MORPHO_COMPLETE_STATUS = 100
#OLD_LEMMAS_COMPLETE_STATUS = 101
#OLD_RUBRICATION_COMPLETE_STATUS = 102

FASTTEXT_EMBEDDING_COMPLETE_STATUS = 105
MORPHO_COMPLETE_STATUS = 110
LEMMAS_COMPLETE_STATUS = 115

NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS = 120

CALC_EMBEDDING_COMPLETE_STATUS = 130
RUBRICATION_COMPLETE_STATUS = 140
CAPITAL_FEATURE_COMPLETE_STATUS = 150

TOMITA_FIRST_COMPLETE_STATUS = 200
NER_TOMITA_FEATURES_COMPLETE_STATUS = 300
OLD_NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS = 301
NER_TOMITA_MORPHO_FEATURES_COMPLETE_STATUS = 302
NER_PREDICT_COMPLETE_STATUS = 350
MARKUP_COMPLETE_STATUS = 400
THEMING_COMPLETE_STATUS = 500
NER_ENTITIES_COMPLETE_STATUS = 850
RUBRICATION_BY_COMPARING_COMPLETE_STATUS = 950
CLEANING_COMPLETE_STATUS = 995
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
BAD_COUNTRY = 2003
SITE_PAGE_PARSE_FAILED = 2004
WITHOUT_ENTITIES = 2005
SITE_PAGE_LOADING_FAILED = 2006
SITE_PAGE_DECODING_FAILED = 2007

mode_times = False
cur_config = "last_config"
logic_times = {}
if sys.argv[0].split("/")[-1] == 'times.py':
    mode_times = True
    cur_config = "test_config"
apps_config = variable_get(cur_config)


def router(doc_id, app_id, status):
    """route function, that adds new tasks by incoming result (document's status)"""
    doc_id = str(doc_id)
    app_conf = apps_config[app_id]
    logging.info("route doc: " + str(doc_id) + " status: " + str(status) + " app_id: " + app_id)
    if status >= 2000:  # ERROR
        if "mode" in app_conf and app_conf["mode"] == "live":
            logging.info("delete doc: " + str(doc_id) + " status: " + str(status) + " app_id: " + app_id)
            session = db_session()
            delete_document(doc_id, session, full=False)
            session.commit()
            session.remove()
        return
    if status in [GOOGLE_NEWS_INIT_STATUS, GOOGLE_ALERTS_INIT_STATUS, YANDEX_NEWS_INIT_STATUS, YANDEX_RSS_INIT_STATUS, CSV_INIT_STATUS, SELECTOR_INIT_STATUS, FROM_CSV_INIT_STATUS, RSS_INIT_STATUS]:  # to find full text of HTML page
        regular_download_page.delay(doc_id, SITE_PAGE_LOADING_COMPLETE_STATUS, app_id=app_id)
        return
    if status == SITE_PAGE_LOADING_COMPLETE_STATUS:  # to readability
        regular_find_full_text.delay(doc_id, SITE_PAGE_READABILITY_COMPLETE_STATUS, app_id=app_id)
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
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        record_id = str(
            session.query(Record).filter_by(source=doc.meta["source_record_id"]).options(load_only("document_id")).first().document_id)
        source_app_id = doc.source_with_type.split(" ")[1]
        source_app_conf = apps_config[source_app_id]
        if "configurator" in source_app_conf:
            doc.url = app_conf["force_url_doomain"] + '/#page=configurator,documentId=' + record_id + ',app=' + source_app_id
        else:
            doc.url = app_conf["force_url_doomain"] + '/#page=inbox,documentId=' + record_id + ',app=' + source_app_id

        session.commit()
        session.remove()
    if "fasttext_embedding" in app_conf and status < FASTTEXT_EMBEDDING_COMPLETE_STATUS :  # to calculate fasttext embedding
        regular_calculate_fasttext_embedding.delay(doc_id, FASTTEXT_EMBEDDING_COMPLETE_STATUS, app_id=app_id)
        return
    if "morpho" in app_conf and status < MORPHO_COMPLETE_STATUS :  # to morpho
        regular_morpho.delay(doc_id, MORPHO_COMPLETE_STATUS, app_id=app_id)
        return
    if "lemmas" in app_conf and status < LEMMAS_COMPLETE_STATUS:  # to lemmas
        regular_lemmas.delay(doc_id, LEMMAS_COMPLETE_STATUS, app_id=app_id)
        return
    if "ner_tomita_embedding_features" in app_conf and status < NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS:  # to preparing lemmas
        regular_embedding_features.delay(doc_id, NER_TOMITA_EMBEDDING_FEATURES_COMPLETE_STATUS, app_id=app_id)
        return
    if "calc_embedding" in app_conf and status < CALC_EMBEDDING_COMPLETE_STATUS:  # to lemmas
        regular_calc_embedding.delay(doc_id, CALC_EMBEDDING_COMPLETE_STATUS, app_id=app_id)
        return
    if "rubrication" in app_conf and status < RUBRICATION_COMPLETE_STATUS:  # to rubrication
        regular_rubrication.delay(app_conf["rubrication"], doc_id, RUBRICATION_COMPLETE_STATUS, WITHOUT_RUBRICS, app_id=app_id)
        return
    if "capital_feature" in app_conf and status < CAPITAL_FEATURE_COMPLETE_STATUS:  # to create capital feature
        regular_capital_feature.delay(doc_id, CAPITAL_FEATURE_COMPLETE_STATUS, app_id=app_id)
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
    if "mode" in app_conf and app_conf["mode"] == "live" and status < CLEANING_COMPLETE_STATUS:
        regular_cleaning.delay(doc_id, CLEANING_COMPLETE_STATUS, app_id=app_id)
        return
    # finish regular procedures:
    session = db_session()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    changed = False
    if "special_type" in app_conf:
        doc.type = app_conf["special_type"]
        changed = True
    if "special_final_status" in app_conf:
        new_status = app_conf["special_final_status"]
    else:
        new_status = REGULAR_PROCESSES_FINISH_STATUS
    if new_status != doc.status:
        doc.status = new_status
        changed = True
    if changed:
        session.commit()
    session.remove()
    return status


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_gn_start_parsing(source_key, **kwargs):
    """parsing google news request"""
    print("GN CRAWL START: "+source_key)
    session = db_session()
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
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка google_news краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
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
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка google_alerts краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
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
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка yandex_news краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='yandex_news', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("YN CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_ya_rss_start_parsing(source_key, **kwargs):
    """parsing yandex rss"""
    print("YR CRAWL START: "+source_key)
    session = db_session()
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["yandex_rss"][source_key]
    blacklist = apps_config[app_id]["blacklist"] if "blacklist" in apps_config[app_id] else []
    try:
        docs = ya_rss_start_parsing(source_key, blacklist, app_id, session)
        for doc in docs:
            doc.status = YANDEX_RSS_INIT_STATUS
            doc.source_with_type = "yandex_rss "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id,  YANDEX_RSS_INIT_STATUS)
    except Exception as err:
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка yandex_rss краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='yandex_rss', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("YR CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_csv_start_parsing(source_key, **kwargs):
    """parsing csv"""
    print("CSV CRAWL START: "+source_key)
    session = db_session()
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
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка csv краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    session.remove()
    print("CSV CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_from_csv_start_parsing(source_key, **kwargs):
    """parsing csv"""
    print("CSV CRAWL START: "+source_key)
    session = db_session()
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["from_csv"][source_key]
    try:
        docs = from_csv_start_parsing(source_key, app_id, session)
        for doc in docs:
            doc.status = FROM_CSV_INIT_STATUS
            doc.source_with_type = "from_csv "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id, CSV_INIT_STATUS)
    except Exception as err:
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка from_csv краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='from_csv',
                                                          source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("FROM CSV CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_selector_start_parsing(source_key, **kwargs):
    """parsing custom site request"""
    print("SELECTOR START: "+source_key)
    session = db_session()
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["selector"][source_key]
    try:
        docs = selector_start_parsing(source_key, source["patterns"], app_id, session)
        for doc in docs:
            doc.status = SELECTOR_INIT_STATUS
            doc.source_with_type = "selector "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id,  SELECTOR_INIT_STATUS)
    except Exception as err:
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка selector краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='selector', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("SELECTOR CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_other_app_start_parsing(source_key, **kwargs):
    """cloning docs from other app"""
    print("OA CRAWL START: "+source_key)
    session = db_session()
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["other_app"][source_key]
    blacklist = apps_config[app_id]["blacklist"] if "blacklist" in apps_config[app_id] else []
    try:
        docs = other_app_cloning(source_key, blacklist, source["fields_to_clone"], source["source_status"], app_id, session)
        for doc in docs:
            doc.status = source["start_status"]
            doc.source_with_type = "other_app "+source_key
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id, source["start_status"])
    except Exception as err:
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка other_app краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    session.remove()
    print("OA CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_refactor_start_parsing(source_key, **kwargs):
    """cloning docs from other app"""
    print("REFACTOR CRAWL START: "+source_key)
    session = db_session()
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["refactor"][source_key]
    status = int(source_key)
    try:
        if "new_status" in source:
            new_status = source["new_status"]
        else:
            new_status = status
        doc_ids = refactor_start_parsing(status, new_status, source["from_date"], app_id, session)
        for doc_id in doc_ids:
            router(doc_id, app_id, new_status)
    except Exception as err:
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка refactor краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    session.remove()
    print("REFACTOR CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_central_start_parsing(source_key, **kwargs):
    """get docs from central server"""
    print("CENTRAL CRAWL START: "+source_key)
    session = db_session()
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["central"][source_key]
    try:
        doc_ids = central_start_parsing(source_key, source["query"], app_id, session)
        session.commit()
        for doc_id in doc_ids:
            router(doc_id, app_id, FASTTEXT_EMBEDDING_COMPLETE_STATUS)
    except Exception as err:
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка central краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='selector', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("REFACTOR CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_rss_start_parsing(source_key, **kwargs):
    """load rsses"""
    print("RSS CRAWL START: "+source_key)
    session = db_session()
    app_id = kwargs["app_id"]
    source = apps_config[app_id]["crawler"]["rss"][source_key]
    countries = apps_config[app_id]["countries"] if "countries" in apps_config[app_id] else []
    try:
        results = rss_start_parsing(source_key, countries, session)

        for result in results:
            regular_one_rss_parsing.delay(result[0].url, result[0].package, str(result[0].publisher_id), result[1].name, app_id)
    except Exception as err:
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка rss краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='rss', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("RSS CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True)
def regular_one_rss_parsing(source_url, package, publisher_id, publisher_name, app_id):
    """parsing site rss"""
    session = db_session()
    try:
        docs = one_rss_parsing(source_url, package, publisher_id, publisher_name, app_id, session)
        for doc in docs:
            doc.status = RSS_INIT_STATUS
            doc.source_with_type = "rss " + package + " " + source_url
            doc.app_id = app_id
        session.commit()
        for doc in docs:
            router(doc.doc_id, app_id, RSS_INIT_STATUS)
    except Exception as err:
        pos = package.find('_')
        kind = "" if pos == -1 else package[pos:]
        pack = package if pos == -1 else package[:pos]
        newkind = "_bad" if type(err).__name__ == 'SoftTimeLimitExceeded' else "_long"
        if newkind != kind:
            source = session.query(Source).filter(Source.url == source_url).first()
            source.package = pack+newkind
            session.commit()
        print_exception()
        # err_txt = repr(err)
        logging.error("Неизвестная ошибка rss краулера, source: " + source_url)
        # print(err_txt)
        print_exception()
    session.remove()



@app.task(ignore_result=True, time_limit=660, soft_time_limit=600)
def regular_vk_start_parsing(source_key, **kwargs):
    """parsing vk request"""
    print("VK CRAWL START: "+source_key)
    session = db_session()
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
        #err_txt = repr(err)
        logging.error("Неизвестная ошибка vk краулера, source: " + source_key)
        #print(err_txt)
        print_exception()
    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type='yandex_news', source_key=source_key).first()
    source_status.ready = True
    source_status.next_crawling_time = datetime.datetime.now().timestamp() + source["period"]
    session.commit()
    session.remove()
    print("VK CRAWL COMPLETE: "+source_key)


@app.task(ignore_result=True)
def regular_vk_parse_item(doc_id, new_status, **kwargs):
    """parsing vk request"""
    session, doc = get_doc(doc_id)
    vk_parse_item(doc)
    set_doc(doc, new_status, session)



@app.task(ignore_result=True)
def regular_download_page(doc_id, new_status, **kwargs):
    """parsing HTML page to find full text"""
    session, doc = get_doc(doc_id)
    try:
        download_page(doc, session)
    except Exception as err:
        err_txt = str(err)
        err_type = type(err)
        error_found = False
        if err_type == HTTPError:
            # print(url, err.code)
            new_status = SITE_PAGE_LOADING_FAILED
            logging.error("Ошибка загрузки код: " + str(err.code) + " doc_id: " + doc_id)  # + " url: " + url)
            error_found = True
        if not error_found:
            # print(url, type(err))
            new_status = SITE_PAGE_DECODING_FAILED
            logging.error("Ошибка декодинга doc_id: " + doc_id + "url:" + doc.url)
        print(err_txt)
        print_exception()
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_find_full_text(doc_id, new_status, **kwargs):
    """parsing HTML page to find full text"""
    session, doc = get_doc(doc_id)
    try:
        app_id = kwargs["app_id"]
        countries = apps_config[app_id]["countries"] if "countries" in apps_config[app_id] else None
        find_full_text(doc, session, countries)
        flag_modified(doc, "meta")
    except Exception as err:
        err_txt = str(err)
        err_type = type(err)
        error_found = False
        if err_type == ValueError:
            if err_txt == 'Empty text':
                logging.error("Пустой текст doc_id: " + doc_id)
                new_status = EMPTY_TEXT
                error_found = True
            elif err_txt == 'Bad country':
                logging.error("Плохая страна doc_id: " + doc_id)
                new_status = BAD_COUNTRY
                error_found = True
        if not error_found:
            # print(url, type(err))
            new_status = SITE_PAGE_PARSE_FAILED
            logging.error("Неизвестная ошибка парсинга doc_id: " + doc_id + "url:" + doc.url)
        print(err_txt)
        print_exception()
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_calculate_fasttext_embedding(doc_id, new_status, **kwargs):
    """calculate fasttext embedding"""
    session, doc = get_doc(doc_id)
    reg_fasttext_embedding(doc)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_morpho(doc_id, new_status, **kwargs):
    """morphologia"""
    session, doc = get_doc(doc_id)
    rb.morpho_doc(doc)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_lemmas(doc_id, new_status, **kwargs):
    """counting lemmas frequency for one document"""
    session, doc = get_doc(doc_id)
    rb.lemmas_freq_doc(doc)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_calc_embedding(doc_id, new_status, **kwargs):
    """calculate paragraph embeddings"""
    session, doc = get_doc(doc_id)
    calc_paragraph_embedding(doc, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_rubrication(rubrics, doc_id, with_rubrics_status, without_rubrics_status, **kwargs):
    """regular rubrication"""
    session, doc = get_doc(doc_id)
    # rb.spot_doc_rubrics2(doc_id, rubrics_for_regular, new_status)
    if "rubrication_type" in rubrics[0] and rubrics[0]["rubrication_type"] == "fasttext":
        rb.fasttext_spot_doc_rubrics(doc, rubrics, session, False)
    else:
        rb.spot_doc_rubrics(doc, rubrics, session, False)

    if len(doc.rubric_ids) == 0:
        new_status = without_rubrics_status
    else:
        new_status = with_rubrics_status
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_capital_feature(doc_id, new_status, **kwargs):
    """create capital feature"""
    session, doc = get_doc(doc_id)
    create_capital_feature(doc, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True,time_limit=190, soft_time_limit=180)
def regular_tomita(grammar, doc_id, new_status, **kwargs):
    """tomita"""
    session, doc = get_doc(doc_id, grammar=grammar)
    run_tomita(doc, grammar, session, False)
    set_doc(doc, new_status, session, grammar=grammar)


@app.task(ignore_result=True)
def regular_tomita_features(grammars, doc_id, new_status, **kwargs):
    """tomita features (transform coordinates for ner)"""
    session, doc = get_doc(doc_id)
    ner_feature.create_tomita_feature(doc, grammars, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_embedding_features(doc_id, new_status, **kwargs):
    """lemmas preparation for NER"""
    session, doc = get_doc(doc_id)
    ner_feature.create_embedding_feature(doc, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_morpho_features(doc_id, new_status, **kwargs):
    session, doc = get_doc(doc_id)
    ner_feature.create_morpho_feature(doc, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True,time_limit=190, soft_time_limit=180)
def regular_NER_predict(ner_settings, doc_id, new_status, **kwargs):
    """NER computing"""
    session, doc = get_doc(doc_id)
    NER_predict(doc, ner_settings, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_create_markup(markup_settings, doc_id, new_status, **kwargs):
    """create entities if it needs and create markup"""
    session, doc = get_doc(doc_id)
    # create_markup(doc, session, False)
    create_markup_regular(doc, markup_settings, session, False)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_theming(doc_id, new_status, **kwargs):
    """regular theming"""
    session, doc = get_doc(doc_id)
    regular_themization(doc, session)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
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
    set_doc(doc, new_status, session)



@app.task(ignore_result=True)
def regular_rubrication_by_comparing(config, doc_id, new_status, **kwargs):
    """rubrication by comparing with clone source"""
    session, doc = get_doc(doc_id)
    reg_rubrication_by_comparing(doc, config, session)
    set_doc(doc, new_status, session)


@app.task(ignore_result=True)
def regular_cleaning(doc_id, new_status, **kwargs):
    """regular cleaning"""
    session, doc = get_doc(doc_id)
    app_id = kwargs["app_id"]
    if "entities_required" in apps_config[app_id] and (not doc.entity_ids or len(doc.entity_ids) == 0):
        new_status = WITHOUT_ENTITIES
    else:
        cleaning_document(doc, session)
    set_doc(doc, new_status, session)


def get_doc(doc_id, **kwargs):
    """reading doc from db"""
    if mode_times:
        caller_name = inspect.stack()[1][3]
        if caller_name == 'regular_tomita':
            caller_name = caller_name+"_"+kwargs["grammar"]
        caller_name = caller_name.replace('regular_', '')
        print("START: "+caller_name)
        logic_times[caller_name] = datetime.datetime.now()
    session = db_session()
    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    return session, doc


def set_doc(doc, new_status, session, **kwargs):
    """writing changes to db"""
    doc.status = new_status
    session.commit()
    doc_id = doc.doc_id
    session.remove()
    if mode_times:
        caller_name = inspect.stack()[1][3]
        if caller_name == 'regular_tomita':
            caller_name = caller_name+"_"+kwargs["grammar"]
        caller_name = caller_name.replace('regular_', '')
        print("FIN: "+caller_name)
        logic_times[caller_name] = (datetime.datetime.now() - logic_times[caller_name]).total_seconds()
        logic_times['total'] = logic_times['total'] + logic_times[caller_name]
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