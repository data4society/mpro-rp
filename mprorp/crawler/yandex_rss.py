"""rss 2.0 parser"""
from lxml import etree
import re
import datetime
import urllib.parse as urlparse

from mprorp.db.models import *

from mprorp.crawler.utils import send_get_request, check_url_with_blacklist
import datetime


def ya_rss_start_parsing(source_url, blacklist, app_id, session):
    """download and parse yandex rss feed"""
    # download yandex rss feed
    req_result = send_get_request(source_url, 'utf-8', has_encoding=True)
    root_xml = etree.fromstring(req_result)
    channel = root_xml.find("channel")
    # print(len(channel.findall("item")))
    items = channel.findall("item")
    docs = []
    guids = []
    for item in items:
        desc = item.find("description").text
        """parses one news item and create new Document object"""
        title = item.find("title").text
        link = item.find("link").text
        url = "http://"+urlparse.parse_qs(urlparse.urlparse(link).query)['cl4url'][0]
        print(url)
        if check_url_with_blacklist(url, blacklist):
            print("BLACKLIST STOP: "+url)
            return
        date_text = item.find("pubDate").text

        date = datetime.datetime.strptime(date_text, "%d %b %Y %H:%M:%S %z")  # 10 Jan 2017 13:16:00 +0300
        #publisher = desc_div.find("font").find("b").find("font").text

        guid = app_id + url
        if guid not in guids and session.query(Document).filter_by(guid=guid).count() == 0:
            # initial insert with guid, start status and reference to source
            guids.append(guid)
            new_doc = Document(guid=guid, url=url, status=0, type='article')
            new_doc.published_date = date
            new_doc.title = title
            meta = dict()
            meta["publisher"] = {}  # {"name": publisher}
            meta["abstract"] = desc
            new_doc.meta = meta

            session.add(new_doc)
            docs.append(new_doc)


if __name__ == '__main__':
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    from mprorp.db.dbDriver import db_session
    session = db_session()
    ya_rss_start_parsing('https://news.yandex.ru/society.rss', [], 'test', session)
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))