"""main entry point"""
from __future__ import absolute_import
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import datetime

from mprorp.crawler.vk import vk_start_parsing


@app.task
def check_sources():
    sources = select(Source.source_id, (Source.parse_period != -1) & (Source.next_crawling_time < datetime.datetime.now())).fetchall()
    print(sources)
    for source in sources:
        vk_start_parsing(source[0])


def router(docstatuses):
    for docstatus in docstatuses:
        doc_id = docstatus["doc_id"]
        status = docstatus["status"]
        """
        if status == 0:
            pass
        if status == 1:
            anton_func(doc_id)
        if status == 1:
            anton_func(doc_id)
        if status == 1:
            anton_func(doc_id)
"""

if __name__ == "__main__":
    check_sources()