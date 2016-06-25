"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
from mprorp.crawler.readability.libs.readability2.readability import Document as Doc
import urllib.request


def find_full_text(url):
    try:
        urllib.request.urlopen(url)
        html_source = urllib.request.urlopen(url).read()  #
        # html_source = send_get_request(url, gen_useragent=True)
        # print(html)
        doc = Doc(html_source)
        content = doc.summary()
        # title = doc.short_title()

        stripped = strip_tags(content)
        stripped = to_plain_text(stripped)
        return stripped
    except BaseException:
        print('ERROR with ' + url)
        return 'ERROR'
