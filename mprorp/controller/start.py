"""start celery task (checking sources)"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from .logic import regular_gn_start_parsing, regular_vk_start_parsing


@app.task(ignore_result=True)
def check_sources():
    #  vk_start_parsing.delay('2c00848d-dc19-4de0-a076-8d89c414a4fd')
    # return
    sources = select([Source.source_id,Source.source_type_id], (Source.parse_period != -1) &
                     (Source.next_crawling_time < datetime.datetime.now()) &
                     (Source.wait == True)).fetchall()
    print("NEED CRAWL: ",sources)
    for source in sources:
        source_obj = Source(source_id=source[0], wait=False)
        update(source_obj)
        source_type = str(source[1])
        if source_type in ['0cc76b0c-531e-4a90-ab0b-078695336df5','81518bd0-9aef-4899-84c5-c1839e155963']: #  vk
            print("START VK CRAWL")
            regular_vk_start_parsing.delay(source[0])
        if source_type in ['1d6210b2-5ff3-401c-b0ba-892d43e0b741', '62cf1ff2-c860-40db-92e6-c3a3898fea48']: #  google_news
            print("START GOOGLE NEWS CRAWL")
            regular_gn_start_parsing.delay(source[0])




if __name__ == "__main__":
    check_sources()