"""lxml readability - phyton library"""
from mprorp.crawler.utils import *
import urllib.request
from mprorp.crawler.readability.libs.breadability.readable import Article


def find_full_text(html_source):
    doc = Article(html_source)
    content = doc.readable

    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    return stripped
