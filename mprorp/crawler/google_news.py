"""google news list and story parser"""
from lxml import etree
from mprorp.celery_app import app
#from mprorp.controller.logic import *
import re
import datetime
import urllib.parse as urlparse

from mprorp.db.dbDriver import *
from mprorp.db.models import *

from mprorp.crawler.utils import send_get_request
import datetime


#@app.task
def gn_start_parsing(source_id):
    """download google news start feed and feeds for every story"""
    # get source url
    [source_url, parse_period] = select([Source.url,Source.parse_period], Source.source_id == source_id).fetchone()
    # download google news start feed
    req_result = send_get_request(source_url,'utf-8')
    root_xml = etree.fromstring(req_result)
    channel = root_xml.find("channel")
    print(len(channel.findall("item")))
    items = channel.findall("item")
    for item in items:
        desc = item.find("description").text
        # find story id for every item
        ncls = re.findall(r'ncl=([A-Za-z0-9-_]+)',desc)
        # if no story id was found we parse item from start feed
        if len(ncls) == 0:
            parseItem(item, source_id)
        else:
            for ncl in ncls:
                # download google news story feed
                req_result = send_get_request('https://news.google.com/news?cf=all&hl=ru&pz=1&ned=ru_ru&scoring=n&cf=all&ncl='+ncl+'&output=rss','utf-8')
                sub_root_xml = etree.fromstring(req_result)
                sub_channel = sub_root_xml.find("channel")
                print(len(sub_channel.findall("item")))
                sub_items = sub_channel.findall("item")
                for sub_item in sub_items:
                    parseItem(sub_item, source_id)

    next_crawling_time = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + parse_period)
    source = Source(source_id = source_id, next_crawling_time = next_crawling_time, wait = True)
    update(source)
    print("GN CRAWL COMPLETE")

def parseItem(item, source_id):
    title = item.find("title").text
    gnews_link = item.find("link").text
    url = urlparse.parse_qs(urlparse.urlparse(gnews_link).query)['url'][0]
    date_text = item.find("pubDate").text

    date = datetime.datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S %Z") #Mon, 13 Jun 2016 14:54:42 GMT
    desc_html = etree.HTML('<html><head></head><body>'+item.find("description").text+'</body></html>')#.replace('<br>','<br />')
    #print(etree.tostring(desc_html, pretty_print=True, method="html"))
    desc_div = desc_html.find("body").find("table").find("tr").find('td[@class="j"]').find("font").find('div[@class="lh"]')
    publisher = desc_div.find("font").find("b").find("font").text
    desc = desc_div.findall("font")[1].text

    pos = title.find(' - '+publisher)
    title = title[:pos]

    if not select(Document.doc_id, Document.guid == url).fetchone():
        print(title)
        print(url)
        print(publisher)
        print(desc)
        print(date)
        # initial insert with guid, start status and reference to source
        new_doc = Document(guid=url, source_id=source_id, status=0, type='article')
        new_doc.published_date = date
        new_doc.title = title
        meta = dict()
        meta["publisher"] = {"name": publisher}
        meta["abstract"] = desc
        new_doc.meta = meta

        insert(new_doc)
        # further parsing
        new_doc_id = new_doc.doc_id
        #findFullText(new_doc_id)
        #router_func(new_doc_id, 1)


if __name__ == '__main__':
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    gn_start_parsing('f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))