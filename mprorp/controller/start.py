"""start celery task (checking sources)"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.controller.logic import regular_gn_start_parsing, regular_ga_start_parsing, \
    regular_ya_rss_start_parsing, regular_vk_start_parsing, regular_yn_start_parsing, \
    regular_csv_start_parsing, regular_other_app_start_parsing, regular_selector_start_parsing, \
    regular_from_csv_start_parsing, regular_refactor_start_parsing, regular_rss_start_parsing#, \
    #regular_central_parsing
from sqlalchemy.orm import load_only


@app.task(ignore_result=True)
def check_sources():
    """check sources and start crawling if need"""
    session = db_session()
    apps_config = variable_get("last_config", 0, session)
    tasks = []
    for app_id in apps_config:
        app = apps_config[app_id]
        if "crawler" in app:
            crawler = app["crawler"]
            for source_type in crawler:
                for source_key in crawler[source_type]:
                    source = crawler[source_type][source_key]
                    source_status = session.query(SourceStatus).filter_by(app_id=app_id, type=source_type, source_key=source_key).first()
                    if source["on"] and source_status.ready and source_status.next_crawling_time < datetime.datetime.now().timestamp():
                        #source["ready"] = False
                        source_status.ready = False
                        """
                        if "clear_old" in source:
                            print(
                                "CLEAR OLD: START DELETING DOCS WHERE APP=" + app_id + " AND TYPE=" + source_type + " AND SOURCE=" + source_key)
                            session.execute(
                                "DELETE FROM mentions r USING markups m, documents d WHERE m.markup_id = r.markup AND m.document = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute(
                                "DELETE FROM public.\"references\" r USING markups m, documents d WHERE m.markup_id = r.markup AND m.document = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute("DELETE FROM markups m USING documents d WHERE m.document = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute("DELETE FROM rubricationresults r USING documents d WHERE r.doc_id = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute("DELETE FROM documentrubrics r USING documents d WHERE r.doc_id = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute("DELETE FROM tomita_results r USING documents d WHERE r.doc_id = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute("DELETE FROM objectfeatures r USING documents d WHERE r.doc_id = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute("DELETE FROM ner_features r USING documents d WHERE r.doc_id = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute(
                                "DELETE FROM changes c USING records r, documents d WHERE c.document_id = r.document_id AND r.source = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute(
                                "DELETE FROM records r USING documents d WHERE r.source = d.doc_id AND d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type+" "+source_key + "'")
                            session.execute(
                                "DELETE FROM documents d WHERE d.app_id = '" + app_id + "' AND d.source_with_type = '" + source_type + " " + source_key + "'")
                            #docs = session.query(Document).filter_by(source_with_type=source_type+" "+source_key).options(load_only("doc_id")).all()
                            print("COMPLETE DELETING DOCS WHERE APP="+app_id+" AND TYPE="+source_type+" AND SOURCE="+source_key)
                            #for doc in docs:
                                #delete_document(str(doc.doc_id), session)
                        """
                        print("ADD " + source_type + " CRAWL " + source_key)
                        if source_type == "vk":  # vk
                            tasks.append([regular_vk_start_parsing, source_key, app_id])
                        elif source_type == "google_news":  # google_news
                            tasks.append([regular_gn_start_parsing, source_key, app_id])
                        elif source_type == "google_alerts":  # google alerts
                            tasks.append([regular_ga_start_parsing, source_key, app_id])
                        elif source_type == "yandex_news":  # yandex news
                            tasks.append([regular_yn_start_parsing, source_key, app_id])
                        elif source_type == "selector":  # selector
                            tasks.append([regular_selector_start_parsing, source_key, app_id])
                        elif source_type == "yandex_rss":  # yandex rss
                            tasks.append([regular_ya_rss_start_parsing, source_key, app_id])
                        elif source_type == "csv_to_rubricator":  # urls with rubrics from csv
                            tasks.append([regular_csv_start_parsing, source_key, app_id])
                        elif source_type == "from_csv":  # urls from csv
                            tasks.append([regular_from_csv_start_parsing, source_key, app_id])
                        elif source_type == "other_app":  # clone from other app
                            tasks.append([regular_other_app_start_parsing, source_key, app_id])
                        elif source_type == "refactor":  # continue working with bad documents
                            tasks.append([regular_refactor_start_parsing, source_key, app_id])
                        elif source_type == "rss":  # rssses from news sites
                            tasks.append([regular_rss_start_parsing, source_key, app_id])
                        #elif source_type == "central":  # documents from central service
                        #    tasks.append([regular_central_parsing, source_key, app_id])
                    elif (not source_status.ready) and source["on"] and source_status.next_crawling_time < datetime.datetime.now().timestamp():
                        print("wait for "+source_key)
    # variable_set("last_config", apps_config)
    session.commit()
    session.remove()
    for task in tasks:
        task[0].delay(task[1], app_id=task[2])


if __name__ == "__main__":
    check_sources()