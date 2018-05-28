"""google news list and story parser"""
from lxml import etree
import re
import datetime
import urllib.parse as urlparse

from mprorp.db.models import *

from mprorp.crawler.utils import send_get_request, check_url_with_blacklist, normalize_url
import datetime


def gn_start_parsing(source_url, blacklist, app_id, session):
    """download google news start feed and feeds for every story"""
    # download google news start feed
    req_result = send_get_request(source_url,'utf-8')
    root_xml = etree.fromstring(req_result)
    channel = root_xml.find("channel")
    # print(len(channel.findall("item")))
    items = channel.findall("item")
    docs = []
    guids = []
    for item in items:
        desc = item.find("description").text
        # find story id for every item
        ncls = re.findall(r'ncl=([A-Za-z0-9-_]+)',desc)
        # if no story id was found we parse item from start feed
        if len(ncls) == 0:
            parse_gn_item(item, blacklist, app_id, session, docs, guids)
        else:
            for ncl in ncls:
                # download google news story feed
                req_result = send_get_request('https://news.google.com/news?cf=all&hl=ru&pz=1&ned=ru_ru&scoring=n&cf=all&ncl='+ncl+'&output=rss','utf-8')
                sub_root_xml = etree.fromstring(req_result)
                sub_channel = sub_root_xml.find("channel")
                # print(len(sub_channel.findall("item")))
                sub_items = sub_channel.findall("item")
                for sub_item in sub_items:
                    parse_gn_item(sub_item, blacklist, app_id, session, docs, guids)

    return docs


def parse_gn_item(item, blacklist, app_id, session, docs, guids):
    """parses one news item and create new Document object"""
    title = item.find("title").text
    gnews_link = item.find("link").text
    url = normalize_url(urlparse.parse_qs(urlparse.urlparse(gnews_link).query)['url'][0])
    if check_url_with_blacklist(url, blacklist):
        print("BLACKLIST STOP: "+url)
        return
    date_text = item.find("pubDate").text

    date = datetime.datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S %Z") #Mon, 13 Jun 2016 14:54:42 GMT
    desc_html = etree.HTML('<html><head></head><body>'+item.find("description").text+'</body></html>')#.replace('<br>','<br />')
    desc_div = desc_html.find("body").find("table").find("tr").find('td[@class="j"]').find("font").find('div[@class="lh"]')
    publisher = desc_div.find("font").find("b").find("font").text
    desc = desc_div.findall("font")[1].text

    pos = title.find(' - '+publisher)
    title = title[:pos]
    guid = app_id + url
    if guid not in guids and session.query(Document).filter_by(guid=guid).count() == 0:
        # initial insert with guid, start status and reference to source
        guids.append(guid)
        new_doc = Document(guid=guid, url=url, status=0, type='article')
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
    gn_start_parsing('f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))