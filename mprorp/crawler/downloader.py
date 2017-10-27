"""working with custom site's page"""
from readability.encoding import get_encoding
from mprorp.crawler.utils import send_get_request

import logging
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'crawler_log.txt')


def download_page(doc, session):
    """download page"""
    url = doc.url
    print('start grabbing ' + url)
    html_source = send_get_request(url, has_encoding=True, gen_useragent=True)

    encoding = get_encoding(html_source) or 'utf-8'
    decoded_page = html_source.decode(encoding, 'replace')
    doc.doc_source = encoding + "|||" + decoded_page
