from requests import Request, Session
from html.parser import HTMLParser


def send_get_request(url, encoding = ''):
    """accessory function for sending requests"""
    s = Session()
    req = Request('GET', url)
    prepped = req.prepare()
    r = s.send(prepped)
    if encoding:
        r.encoding = encoding
    return r.text


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def to_plain_text(txt):
    lines = txt.split("\n")
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]

    return "\n".join(lines)

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)