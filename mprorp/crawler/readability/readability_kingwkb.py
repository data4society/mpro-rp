"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
from mprorp.crawler.readability.libs.kingwkb.readability import Readability
import urllib.request
import urllib3


def find_full_text(url):
    #try:
        #html_source = urllib3.urlopen(url).read().decode('utf-8')
        html_source = urllib.request.urlopen(url).read().decode('utf-8')
        print(html_source)
        # html_source = send_get_request(url, gen_useragent=True)
        readability = Readability(html_source, url)
        content = readability.content
        # title = doc.short_title()

        stripped = strip_tags(content)
        stripped = to_plain_text(stripped)
        return stripped
   # except BaseException:
    #    print('ERROR with ' + url)
    #    return 'ERROR'
