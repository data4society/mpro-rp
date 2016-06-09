from lxml import etree
from mprorp.celery_app import app
from mprorp.controller.logic import *

from mprorp.db.dbDriver import *
from mprorp.db.models import *

from requests import Request, Session
import json
import datetime

def send_get_request(url):
    """accessory function for sending requests"""
    s = Session()
    req = Request('GET', url)
    prepped = req.prepare()
    r = s.send(prepped)
    r.encoding = 'utf-8'
    return r.text

@app.task
def gn_start_parsing(source_id):
    """download vk response and run list parsing function"""
    # get source url
    [source_url, parse_period] = select([Source.url,Source.parse_period], Source.source_id == source_id).fetchone()
    # download vk response
    req_result = send_get_request(source_url)
    print(req_result)
    root_xml = etree.fromstring(req_result)

    print(etree.tostring(root_xml))
    # run list parsing function
    #vk_parse_list(req_result, source_id)
    # change next timestamp crawl start
    next_crawling_time = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + parse_period)
    source = Source(source_id = source_id, next_crawling_time = next_crawling_time, wait = True)
    update(source)
    print("GN CRAWL COMPLETE")

if __name__ == '__main__':
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    gn_start_parsing('f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))