from requests import Request, Session


def send_get_request(url, encoding = ''):
    """accessory function for sending requests"""
    s = Session()
    req = Request('GET', url)
    prepped = req.prepare()
    r = s.send(prepped)
    if encoding:
        r.encoding = encoding
    return r.text
