"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
#from mprorp.crawler.readability.libs.readability2.readability2 import Document as Doc
from mprorp.crawler.readability.readability_fusion import Document as Doc
import urllib.request


def find_full_text(html_source, title="", fusion_clearing = True):
    doc = Doc(html_source)
    content = doc.summary(title=title, fusion_clearing=fusion_clearing)
    confidence = doc.get_confidence()
    #print(confidence)

    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    return stripped, confidence
