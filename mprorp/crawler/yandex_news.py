"""yandex news mail parser"""

from imaplib import IMAP4, IMAP4_SSL
from mprorp.db.models import *
import datetime
import lxml.html
import re


def yn_start_parsing(source, app_id, session):
    """download google news start feed and feeds for every story"""

    server = IMAP4_SSL('imap.yandex.ru')
    (user,password) = source.split(":")
    server.login(user, password)

    server.select()
    rv, data = server.search(None, '(UNSEEN)')
    docs = []
    if rv != 'OK':
        # print("No messages found!")
        return docs
    for num in data[0].split():
        num = num.decode("utf-8")
        rv1, data1 = server.fetch(num, '(RFC822)')
        if rv1 != 'OK':
            #print("ERROR getting message", num)
            continue
        mail = data1[0][1].decode("utf-8")
        if 'Яндекс.Новости' in mail:
            html_start = mail.find('<html>')
            html_mail = mail[html_start:]
            tree_mail = lxml.html.document_fromstring(html_mail)
            ol = tree_mail.find("body").find("ol")
            items = ol.findall("li")
            for item in items:
                parse_yn_item(item, app_id, session, docs)
    print("YN CRAWL COMPLETE")
    return docs

def parse_yn_item(item, app_id, session, docs):
    a = item.find("a")
    url = a.get("href")
    title = a.text_content()
    title = re.sub(r'(\r\n|\n|\r)+', ' ', title)
    date_and_source = item.find("font").text
    punkt_pos = date_and_source.find(', ')
    publisher = date_and_source[punkt_pos+2:]
    date = date_and_source[:punkt_pos]
    date = datetime.datetime.strptime(date, "%d.%m.%Y - %H:%M")
    desc = item.find("p").text_content()
    desc = re.sub(r'(\r\n|\n|\r)+', ' ', desc)
    #print(url)
    #print(publisher)
    #print(date)
    #print(title)
    #print(desc)
    if session.query(Document).filter_by(guid=app_id + url).count() == 0:
        # initial insert with guid, start status and reference to source
        new_doc = Document(guid=app_id + url, url=url, status=0, type='article')
        new_doc.published_date = date
        new_doc.title = title
        meta = dict()
        meta["publisher"] = {"name": publisher}
        meta["abstract"] = desc
        new_doc.meta = meta

        session.add(new_doc)
        docs.append(new_doc)


if __name__ == '__main__':
    from mprorp.db.dbDriver import *
    session = db_session()
    yn_start_parsing('bbe11a5e-07b5-4937-a413-3a858326ccdd', session)
    #session.commit()
    #session.remove()