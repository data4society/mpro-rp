"""working with custom site's page"""
from mprorp.db.dbDriver import *
from mprorp.db.models import *

from mprorp.crawler.readability.readability_fusion import Document as Doc
from mprorp.crawler.utils import *

import urllib.request
import urllib.parse as urlparse

from mprorp.crawler.utils import send_get_request


import logging
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'crawler_log.txt')


def find_full_text(doc):
    """finds full text for doc object by readability algorithm"""
    url = doc.url
    meta = doc.meta
    print('start grabbing ' + url)
    html_source = send_get_request(url, has_encoding=True, gen_useragent=True)# urllib.request.urlopen(url, timeout=10).read()
    #print(html_source.decode("utf-8"))
    rf_doc = Doc(html_source)
    title = doc.title
    if title == None:
        title = ''
    content, doc.title = rf_doc.summary(title=title)

    if content.strip() == '':
        logging.error("Получен пустой текст url: " + url)
        content = meta["abstract"]

    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    parsed_url = urlparse.urlparse(url)
    publisher_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
    meta["publisher"]['url'] = publisher_url

    if stripped == '':
        raise ValueError('Empty text')

    doc.doc_source = content
    doc.stripped = stripped
    doc.meta = meta



if __name__ == '__main__':

    find_full_text(Document(url="http://echo-oren.ru/2016/09/16/11327",meta=dict()))
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