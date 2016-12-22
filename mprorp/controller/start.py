"""start celery task (checking sources)"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.controller.logic import regular_gn_start_parsing, regular_ga_start_parsing, regular_vk_start_parsing, regular_yn_start_parsing, regular_csv_start_parsing, regular_other_app_start_parsing
from sqlalchemy.orm import load_only


@app.task(ignore_result=True)
def check_sources():
    """check sources and start crawling if need"""
    session = db_session()
    apps_config = variable_get("last_config", 0, session)
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
                        if "clear_old" in source:
                            docs = session.query(Document).filter_by(source_with_type=source_type+" "+source_key).options(load_only("doc_id")).first()
                            print("CLEAR OLD: DELETING "+len(docs)+" DOCS WHERE TYPE="+source_type+" AND SOURCE="+source_key)
                            for doc in docs:
                                delete_document(str(doc.doc_id),session)

                        print("ADD " + source_type + " CRAWL " + source_key)
                        if source_type == "vk":  # vk
                            regular_vk_start_parsing.delay(source_key, app_id=app_id)
                        elif source_type == "google_news":  # google_news
                            regular_gn_start_parsing.delay(source_key, app_id=app_id)
                        elif source_type == "google_alerts":  # google alerts
                            regular_ga_start_parsing.delay(source_key, app_id=app_id)
                        elif source_type == "yandex_news":  # yandex news
                            regular_yn_start_parsing.delay(source_key, app_id=app_id)
                        elif source_type == "csv_to_rubricator":  # csv
                            regular_csv_start_parsing.delay(source_key, app_id=app_id)
                        elif source_type == "other_app":  # clone from other app
                            regular_other_app_start_parsing.delay(source_key, app_id=app_id)
                    elif (not source_status.ready) and source["on"] and source_status.next_crawling_time < datetime.datetime.now().timestamp():
                        print("wait for "+source_key)
    # variable_set("last_config", apps_config)
    session.commit()
    session.remove()




if __name__ == "__main__":
    check_sources()