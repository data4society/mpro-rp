"""start celery task (checking sources)"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.controller.logic import regular_gn_start_parsing, regular_ga_start_parsing, regular_vk_start_parsing, regular_yn_start_parsing, regular_csv_start_parsing
from sqlalchemy.orm import load_only


@app.task(ignore_result=True)
def check_sources():
    """check sources and start crawling if need"""
    apps_config = variable_get("last_config")
    for app_id in apps_config:
        app = apps_config[app_id]
        if "crawler" in app:
            crawler = app["crawler"]
            for source_type in crawler:
                for source_key in crawler[source_type]:
                    source = crawler[source_type][source_key]
                    if source["on"] and source["ready"] and source["next_crawling_time"] < datetime.datetime.now().timestamp():
                        source["ready"] = False
                        print("ADD "+source_type+" CRAWL "+source_key)
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
                    elif (not source["ready"]) and source["on"] and source["next_crawling_time"] < datetime.datetime.now().timestamp():
                        print("wait for "+source_key)
    variable_set("last_config", apps_config)




if __name__ == "__main__":
    check_sources()