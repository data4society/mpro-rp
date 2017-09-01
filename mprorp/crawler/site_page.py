"""working with custom site's page"""
from mprorp.db.dbDriver import *
from mprorp.db.models import *

from mprorp.crawler.readability.readability_fusion import Document as Doc
from mprorp.crawler.utils import *

import urllib.request
import urllib.parse as urlparse

from mprorp.crawler.utils import send_get_request
from mprorp.data.ya_smi import add_new_source

from readability.encoding import get_encoding
from readability.compat import str_
from lxml.html import document_fromstring, HTMLParser


import logging
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'crawler_log.txt')


def download_page(doc, session):
    """download page"""
    url = doc.url
    print('start grabbing ' + url)
    html_source = send_get_request(url, has_encoding=True, gen_useragent=True)

    encoding = get_encoding(html_source) or 'utf-8'
    decoded_page = html_source.decode(encoding, 'replace')
    doc.source = encoding + "|||" + decoded_page


def find_full_text(doc, session, countries):
    """finds full text for doc object by readability algorithm"""
    print('start readability ' + doc.url)
    decoded_page = doc.source
    pos = decoded_page.find("|||")
    encoding = decoded_page[:pos]
    decoded_page = decoded_page[pos + 3:]
    utf8_parser = HTMLParser(encoding='utf-8')
    byte_source = document_fromstring(decoded_page.encode('utf-8', 'replace'), parser=utf8_parser)

    readability_and_meta(doc, session, byte_source, encoding, countries)


def readability_and_meta(doc, session, byte_source, encoding, countries):
    url = doc.url
    meta = doc.meta
    #print(html_source.decode("utf-8"))
    rf_doc = Doc(byte_source, encoding)
    title = doc.title
    if title == None:
        title = ''
    content, doc.title, page_meta = rf_doc.summary(title=title)

    if content.strip() == '':
        logging.error("Получен пустой текст url: " + url)
        content = meta["abstract"]

    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    parsed_url = urlparse.urlparse(url)
    publisher_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
    meta["publisher"]['url'] = publisher_url
    meta["page_meta"] = page_meta
    publisher_name = doc.meta["publisher"]["name"]
    publisher = session.query(Publisher).filter_by(name=publisher_name).first()
    if publisher:
        doc.publisher_id = str(publisher.pub_id)
    else:
        publisher = add_new_source(publisher_name)
        if publisher:
            doc.publisher = publisher
            session.add(publisher)
    if countries and publisher and publisher.country not in countries:
        raise ValueError('Bad country')

    if stripped == '':
        raise ValueError('Empty text')

    doc.doc_source = content
    doc.stripped = stripped
    doc.meta = meta


if __name__ == '__main__':
    print("start")
    exit()
    session = db_session()
    docs = session.query(Document).filter_by(app_id='ovd_ideal').all()
    for doc in docs:
        print(doc.meta["publisher"])
        publisher = session.query(Publisher).filter_by(name=doc.meta["publisher"]["name"]).first()
        if publisher:
            print(publisher.name)
            doc.publisher_id = str(publisher.pub_id)
        else:
            print("NONE")
    session.commit()
    session.remove()
    exit()
    session = db_session()
    doc_id = str(session.query(Record).filter_by(document_id='810fd23b-0449-fcb4-2ab4-a4d3e47e5c47').first().source)

    doc = session.query(Document).filter_by(doc_id=doc_id).first()
    find_full_text(doc)
    print(doc.stripped)

    exit()
    articles = select(Document.doc_id, Document.source_id == '71dc5343-c27d-44bf-aa76-f4d8085317fe').fetchall()
    print(len(articles))
    from mprorp.controller.logic import SITE_PAGE_COMPLETE_STATUS, SITE_PAGE_LOADING_FAILED
    #articles = select(Document.doc_id, Document.guid == 'http://u-news24.com/archives/18306').fetchall()
    for article_id in articles:
        find_full_text(article_id[0], SITE_PAGE_COMPLETE_STATUS, SITE_PAGE_LOADING_FAILED)
    #print(articles)
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))