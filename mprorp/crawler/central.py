"""bad documents as crawler source"""
from mprorp.crawler.utils import *
from mprorp.db.models import *
from mprorp.db.dbDriver import *
import datetime

from requests import Request, Session
import json


def central_start_parsing(ip, sql_query, app_id, session):
    """get all docs by condition and set status"""

    from_date = variable_get("last_date_for_"+ip+"_"+app_id, str(datetime.datetime.now()), session)
    url = 'http://'+ip+'/api/last_docs'
    docs = []
    s = Session()
    raw_data = {}
    raw_data["date"] = from_date
    raw_data["sql_query"] = sql_query
    data = json.dumps(raw_data, ensure_ascii=False).encode('utf8').decode('Latin-1')
    # print(data)
    req = Request('POST', url, data=data)
    prepped = req.prepare()
    prepped.headers['Content-Type'] = 'application/json'
    r = s.send(prepped)
    txt = r.text
    ans = json.loads(txt)
    response = ans['response']
    for elem in response:
        doc = Document()
        for prop in elem:
            setattr(doc, prop, elem[prop])
        doc.app_id = app_id
        docs.append(doc)
        session.add(doc)
    variable_set("last_date_for_"+ip+"_"+app_id, max([doc.created for doc in docs]), session)
    doc_ids = [doc.doc_id for doc in docs]
    return doc_ids


if __name__ == '__main__':
    pass