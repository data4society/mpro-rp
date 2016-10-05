"""google news list and story parser"""
from lxml import etree
import re
import datetime
import urllib.parse as urlparse
from mprorp.crawler.utils import *

from mprorp.db.models import *

from mprorp.crawler.utils import send_get_request
import datetime


def ga_start_parsing(source_id, session):
    """download google news start feed and feeds for every story"""
    # get source url
    source = session.query(Source).filter_by(source_id=source_id).first()
    # download google news start feed
    req_result = send_get_request(source.url,has_encoding=True)
    root_xml = etree.fromstring(req_result)

    #print(len(root_xml.findall("{http://www.w3.org/2005/Atom}entry")))
    items = root_xml.findall("{http://www.w3.org/2005/Atom}entry")
    docs = []
    for item in items:
        # if no story id was found we parse item from start feed
        parse_ga_item(item, source_id, session, docs)


    source.next_crawling_time = datetime.datetime.fromtimestamp(
        datetime.datetime.now().timestamp() + source.parse_period)
    source.wait = True
    print("GNA CRAWL COMPLETE")
    return docs


def parse_ga_item(item, source_id, session, docs):
    """parses one news item and create new Document object"""
    title = strip_tags('<html><body>' + item.find("{http://www.w3.org/2005/Atom}title").text + '</body></html>')
    gnews_link = item.find("{http://www.w3.org/2005/Atom}link").get("href")
    parsed_uri = urlparse.urlparse(gnews_link)
    url = urlparse.parse_qs(parsed_uri.query)['url'][0]
    parsed_uri = urlparse.urlparse(url)
    publisher = parsed_uri.netloc
    date_text = item.find("{http://www.w3.org/2005/Atom}published").text
    date = datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ") #2016-10-04T00:56:15Z
    desc = strip_tags('<html><body>' + item.find("{http://www.w3.org/2005/Atom}content").text + '</body></html>')


    if session.query(Document).filter_by(guid=url).count() == 0:
        # initial insert with guid, start status and reference to source
        new_doc = Document(guid="ga_" + url, source_id=source_id, status=0, type='article')
        new_doc.published_date = date
        new_doc.title = title
        meta = dict()
        meta["publisher"] = {"name": publisher}
        meta["abstract"] = desc
        new_doc.meta = meta

        session.add(new_doc)
        docs.append(new_doc)


if __name__ == '__main__':
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    ga_start_parsing('https://www.google.ru/alerts/feeds/01670104253645512148/17155994496834907056') #f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))