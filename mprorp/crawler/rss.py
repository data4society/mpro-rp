"""rss 2.0 parser"""
from lxml import etree

from mprorp.db.dbDriver import db_session
from mprorp.db.models import *

from mprorp.crawler.utils import send_get_request, check_url_with_blacklist, normalize_url
import dateparser
import re


def rss_start_parsing(package, countries, session):
    results = session.query(Source, Publisher).join(Publisher, Source.publisher).filter(Source.source_type == 'rss')\
        .filter(Source.package == package).filter(Publisher.country.in_(countries)).all()
    return results


def one_rss_parsing(source_url, package, publisher_id, publisher_name, app_id, session):
    """download and parse rss feed"""
    docs = []
    # download rss feed
    req_result, txt, status_code = send_get_request(source_url, 'utf-8', gen_useragent=True, has_encoding=True, content_text_status=True)
    req_result = re.sub(b"(<rss[^>]*)(xmlns=\".+?\")([^>]*>)", r"\1\3",  req_result)
    req_result = re.sub(b"(<\?xml[^>]*encoding=\")([^\"]*?)([A-Za-z0-9\-]+)([^\"]*)(\"[^>]*>)", r"\1\3\5",  req_result)
    pos = package.find('_')
    kind = "" if pos == -1 else package[pos:]
    pack = package if pos == -1 else package[:pos]
    bad = False
    long = False
    if status_code == 404:
        bad = True
    elif status_code == 503:
        long = True
    elif txt.find('<channel') == -1:
        if txt.find('Ошибка') == -1 and txt.find('Error') == -1:
            bad = True
        else:
            long = True
    elif len(req_result) > 200000:
        long = True
    newkind = "_bad" if bad else "_long" if long else ""
    if newkind != kind:
        source = session.query(Source).filter(Source.url == source_url).first()
        source.package = pack+newkind
        if newkind != "":
            return docs
    root_xml = etree.fromstring(req_result)
    channel = root_xml.find("channel")
    items = channel.findall("item")
    items_by_links = {app_id + normalize_url(item.find("link").text.strip('\n\t')): item for item in items}
    guids = list(items_by_links.keys())
    if guids:
        q = session.query(Document.guid).filter(Document.guid.in_(guids))
        result = q.all()
        result = [res[0] for res in result]
        items = [items_by_links[key] for key in items_by_links if key not in result]
    for item in items:
        url = normalize_url(item.find("link").text.strip('\n\t'))
        title = item.find("title").text.strip('\n\t')
        date_text = item.find("pubDate").text
        date = dateparser.parse(date_text)
        new_doc = Document(guid=app_id + url, url=url, status=0, type='article', publisher_id=publisher_id)
        new_doc.published_date = date
        new_doc.title = title
        meta = dict()
        meta["publisher"] = {"name": publisher_name}
        description = item.find("descripton")
        if description:
            meta["abstract"] = description.text.strip('\n\t')
        new_doc.meta = meta
        session.add(new_doc)
        docs.append(new_doc)

    return docs


if __name__ == '__main__':
    pass