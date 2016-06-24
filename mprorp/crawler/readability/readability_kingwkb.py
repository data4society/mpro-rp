"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
import mprorp.crawler.readability.libs.kingwkb.readability


def find_full_text(url):
    htmlcode = urllib2.urlopen(url).read().decode('utf-8')
    readability = Readability(htmlcode, url)
    print
    readability.title
    print
    return readability.content
