"""rss 2.0 parser"""
from lxml import etree

from mprorp.db.dbDriver import db_session
from mprorp.db.models import *

from mprorp.crawler.utils import send_get_request, check_url_with_blacklist
import datetime


def rss_start_parsing(package, countries, session):
    results = session.query(Source, Publisher).join(Publisher, Source.publisher).filter(Source.source_type == 'rss')\
        .filter(Source.package == package).filter(Publisher.country.in_(countries)).all()
    return results


def one_rss_parsing(source_url, publisher_id, publisher_name, app_id, session):
    """download and parse yandex rss feed"""
    docs = []
    # download yandex rss feed
    req_result = send_get_request(source_url, 'utf-8', has_encoding=True)
    root_xml = etree.fromstring(req_result)
    channel = root_xml.find("channel")
    items = channel.findall("item")
    items_by_links = {app_id + item.find("link").text: item for item in items}
    guids = list(items_by_links.keys())
    if guids:
        result = session.query(Document.guid).filter(Document.guid.in_(guids)).all()
        result = [res[0] for res in result]
        items = [items_by_links[key] for key in items_by_links if key not in result]
    for item in items:
        url = item.find("link").text
        title = item.find("title").text
        date_text = item.find("pubDate").text
        date = datetime.datetime.strptime(date_text, "%d %b %Y %H:%M:%S %z")  # 10 Jan 2017 13:16:00 +0300
        new_doc = Document(guid=app_id + url, url=url, status=0, type='article', publisher_id=publisher_id)
        new_doc.published_date = date
        new_doc.title = title
        meta = dict()
        meta["publisher"] = {"name": publisher_name}
        description = item.find("descripton")
        if description:
            meta["abstract"] = description.text
        new_doc.meta = meta
        session.add(new_doc)
        docs.append(new_doc)

    return docs


if __name__ == '__main__':
    pass