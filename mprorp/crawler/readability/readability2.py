"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
#from mprorp.crawler.readability.libs.readability2.readability2 import Document as Doc
from mprorp.crawler.readability.readability_fusion import Document as Doc
import urllib.request


def find_full_text(html_source, title="", fusion_clearing = True):
    html_source = html_source.replace(b' </a>', b'</a> ')
    doc = Doc(html_source)
    content, title, page_meta = doc.summary(title=title, fusion_clearing=fusion_clearing)
    confidence = doc.get_confidence()
    #print(title)

    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    return stripped, title, confidence
