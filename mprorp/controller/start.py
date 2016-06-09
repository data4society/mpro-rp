"""main entry point"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.crawler.vk import *

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
    print("NEED CRAWL",sources)
    for source in sources:
        source_obj = Source(source_id=source[0], wait=False)
        update(source_obj)
        if source[1] == '': #  vk
            vk_start_parsing.delay(source[0])




if __name__ == "__main__":
    check_sources()