"""start celery task (checking sources)"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.controller.logic import regular_gn_start_parsing, regular_ga_start_parsing, regular_vk_start_parsing, regular_yn_start_parsing, apps_config
from sqlalchemy.orm import load_only


@app.task(ignore_result=True)
def check_sources():
    """check sources and start crawling if need"""
    for app_id in apps_config:
        app = apps_config[app_id]
        if "crawler" in app:
            crawler = app["crawler"]
            for source_type in crawler:
                for source in crawler[source_type]:
                    source_params = crawler[source_type][source]
                    if source_params["wait"] and source_params["next_crawling_time"] < datetime.datetime.now().timestamp():
                        source_params["wait"] = False
                        if source_type == "vk":  # vk
                            print("START VK CRAWL")
                            regular_vk_start_parsing.delay(source, app_id)
                        elif source_type == "google_news":  # google_news
                            print("START GOOGLE NEWS CRAWL")
                            regular_gn_start_parsing.delay(source, app_id)
                        elif source_type == "google_alerts":  # google alerts
                            print("START GOOGLE ALERTS CRAWL")
                            regular_ga_start_parsing.delay(source, app_id)
                        elif source_type == "yandex_news":  # yandex news
                            print("START YANDEX NEWS CRAWL")
                            regular_yn_start_parsing.delay(source, app_id)
                    elif (not source_params["wait"]) and source_params["next_crawling_time"] < datetime.datetime.now().timestamp():
                        print("wait for "+source)




if __name__ == "__main__":
    check_sources()