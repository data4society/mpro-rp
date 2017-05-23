"""selector parser"""
from urllib.parse import urljoin
import urllib.parse as urlparse

from mprorp.db.dbDriver import *
from mprorp.db.models import *
from readability.htmls import build_doc
from mprorp.crawler.utils import *
from sqlalchemy import or_


def selector_start_parsing(source_url, link_patterns, app_id, session, test_mode=False):
    """parse custom page, find link and add publish, if it needs"""
    domain = domain_from_path(source_url)
    publisher = session.query(Publisher).filter(or_(Publisher.site.like('%//'+domain+'%'), Publisher.site.like('%www.'+domain+'%'))).first()
    parsed_url = urlparse(source_url)
    publisher_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
    if not publisher:
        publisher = Publisher(name=domain, site=publisher_url)
        session.add(publisher)
    html_source = send_get_request(source_url, has_encoding=True, gen_useragent=True)
    doc, encoding = build_doc(html_source)
    links = doc.xpath('//a/@href')
    links = [urljoin(source_url, path_clear(link)) for link in links]

    docs = []
    guids = []
    for link_pattern in link_patterns:
        link_pattern = domain_clear(link_pattern)+"/?$"
        link_pattern = link_pattern.replace('.', '\.')
        link_pattern = link_pattern.replace('(digits)', '\d+')
        link_pattern = link_pattern.replace('(text)', '[^/]+')
        link_pattern = link_pattern.replace('(anytext)', '.*')
        pattern = re.compile(link_pattern)
        pat_links = [link for link in links if pattern.match(domain_clear(link))]
        if test_mode:
            print(link_pattern)
            return pat_links
        #print(doc.xpath("//a[starts-with(@href, '/"+link_pattern+"')]/@href"))
        for link in pat_links:
            add_item(link, publisher, app_id, session, docs, guids)
    return docs


def add_item(url, publisher, app_id, session, docs, guids):
    """parses one news item and create new Document object"""
    guid = app_id + url
    if guid not in guids and session.query(Document).filter_by(guid=guid).count() == 0:
        # initial insert with guid, start status and reference to source
        guids.append(guid)
        new_doc = Document(guid=guid, url=url, status=0, type='article')
        meta = dict()
        meta["publisher"] = {"name": publisher.name}
        new_doc.meta = meta

        session.add(new_doc)
        docs.append(new_doc)


if __name__ == '__main__':
    pass
