"""main entry point"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.crawler.vk import *
from mprorp.crawler.google_news import *

if "worker" in sys.argv:
    celery = True
else:
    celery = False

@app.task
def check_sources():
    #vk_start_parsing.delay('2c00848d-dc19-4de0-a076-8d89c414a4fd')
    #return
    sources = select([Source.source_id,Source.source_type_id], (Source.parse_period != -1) &
                     (Source.next_crawling_time < datetime.datetime.now()) &
                     (Source.wait == True)).fetchall()
    print("NEED CRAWL: ",sources)
    for source in sources:
        source_obj = Source(source_id=source[0], wait=False)
        update(source_obj)
        source_type = str(source[1])
        if source_type == '0cc76b0c-531e-4a90-ab0b-078695336df5': #  vk
            print("START VK CRAWL")
            vk_start_parsing.delay(source[0])
        if source[1] == '1d6210b2-5ff3-401c-b0ba-892d43e0b741': #  google_news
            gn_start_parsing.delay(source[0])




if __name__ == "__main__":
    check_sources()