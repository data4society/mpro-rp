"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
import urllib.request
import breadability.readable as breadable


def find_full_text(url):
    try:
        urllib.request.urlopen(url)
        html_source = urllib.request.urlopen(url).read()  #
        # html_source = send_get_request(url, gen_useragent=True)
        # print(html)
        doc = breadable.Article(html_source)
        content = doc.readable
        # title = doc.short_title()

        stripped = strip_tags(content)
        stripped = to_plain_text(stripped)
        return stripped
    except BaseException:
        print('ERROR with ' + url)
        return 'ERROR'
