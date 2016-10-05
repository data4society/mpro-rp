"""start celery task (checking sources)"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.controller.logic import regular_gn_start_parsing, regular_ga_start_parsing, regular_vk_start_parsing
from sqlalchemy.orm import load_only


@app.task(ignore_result=True)
def check_sources():
    """check sources and start crawling if need"""
    sources_dict = {}
    session = db_session()
    sources = session.query(Source)\
        .filter(Source.parse_period != -1, Source.next_crawling_time < datetime.datetime.now(), Source.wait == True) \
        .options(load_only("source_id", "source_type_id")).all()
    for source in sources:
        sources_dict[str(source.source_id)] = str(source.source_type_id)
    session.query(Source) \
        .filter(Source.parse_period != -1, Source.next_crawling_time < datetime.datetime.now(), Source.wait == True)\
        .update({"wait":False})
    session.commit()
    session.remove()
    for source_id, source_type_id in sources_dict.items():
        print("NEED CRAWL: ", source_id)

        if source_type_id in ['0cc76b0c-531e-4a90-ab0b-078695336df5','81518bd0-9aef-4899-84c5-c1839e155963']: #  vk
            print("START VK CRAWL")
            regular_vk_start_parsing.delay(source_id)
        if source_type_id in ['1d6210b2-5ff3-401c-b0ba-892d43e0b741', '62cf1ff2-c860-40db-92e6-c3a3898fea48']: #  google_news
            print("START GOOGLE NEWS CRAWL")
            regular_gn_start_parsing.delay(source_id)
        if source_type_id in ['ce81b5dc-115c-400b-8886-91f9246926ca']: #  google alerts
            print("START GOOGLE ALERTS CRAWL")
            regular_ga_start_parsing.delay(source_id)


if __name__ == "__main__":
    check_sources()