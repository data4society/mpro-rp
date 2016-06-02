"""main entry point"""
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import datetime
from mprorp.crawler.vk import vk_start_parsing



def check_sources():
    sources = select(Source.source_id, (Source.parse_period != -1) & (Source.next_crawling_time < datetime.datetime.now())).fetchall()
    print(sources)
    for source in sources:
        vk_start_parsing(source[0])

if __name__ == "__main__":
    check_sources()