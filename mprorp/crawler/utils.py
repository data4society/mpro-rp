"""some extra functions"""
from requests import Request, Session
from html.parser import HTMLParser
import re
from user_agent import generate_user_agent, generate_navigator


def send_get_request(url, encoding = '', gen_useragent = False):
    """accessory function for sending requests"""
    s = Session()
    req = Request('GET', url)
    prepped = req.prepare()
    if gen_useragent:
        prepped.headers['User-Agent'] = generate_user_agent()  #'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36 OPR/38.0.2220.31'#generate_user_agent()
        """
        prepped.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        prepped.headers['Accept-Encoding'] = 'gzip, deflate, sdch'
        prepped.headers['Accept-Language'] = 'en-US,en;q=0.8,ru;q=0.6'
        prepped.headers['Connection'] = 'keep-alive'
        prepped.headers['Upgrade-Insecure-Requests'] = '1'
        """
    r = s.send(prepped)
    if encoding:
        r.encoding = encoding
    return r.text


def strip_tags(html):
    """strips text from tags"""
    html = re.sub(r'(<br ?/?>|</p>|</div>)',r'\n\1', html, 0, re.IGNORECASE)
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def to_plain_text(txt):
    """trims and strips text from empty strings"""
    txt = txt.replace(u'\xa0', u' ')  # kill non-breaking space
    lines = txt.split("\n")
    lines = [line.strip('\t\n\r').strip() for line in lines]
    lines = [line for line in lines if line]
    return "\n".join(lines)

class MLStripper(HTMLParser):
    """accessory class for stripping"""
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)