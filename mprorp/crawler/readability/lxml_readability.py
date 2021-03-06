"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
from readability.readability import Document as Doc
import urllib.request


def find_full_text(html_source):
    doc = Doc(html_source)
    content = doc.summary()

    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    return stripped
