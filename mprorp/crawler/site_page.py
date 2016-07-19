from mprorp.db.dbDriver import *
from mprorp.db.models import *

from mprorp.crawler.readability.readability_fusion import Document as Doc
from mprorp.crawler.utils import *

import urllib.request
from urllib.error import *
import urllib.parse as urlparse

import json
import html

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'crawler_log.txt')


def find_full_text(doc):#, failed_status): #, wks):
    url = doc.guid
    meta = doc.meta
    print('start grabbing ' + url)
    """
    res = send_get_request(req_url) # urllib.request.urlopen(url).read().decode('unicode-escape')# send_get_request(url).decode('unicode-escape')
    json_obj = json.loads(res)

    #print(res)

    if "error" in json_obj:
        #need logging
        return;
    if "title" in json_obj:
        print(json_obj["title"])
    content = json_obj["content"]
    content = html.unescape(content)
    #print(content)
    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    print(stripped)
    """

    html_source = urllib.request.urlopen(url, timeout=10).read()
    doc = Doc(html_source)
    content = doc.summary()

    if content.strip() == '':
        logging.error("Получен пустой текст url: " + url)
        content = meta["abstract"]

    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    parsed_url = urlparse.urlparse(url)
    publisher_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
    meta["publisher"]['url'] = publisher_url
    #print(content)
    #print(stripped)
    #print(meta)

    if stripped == '':
        raise ValueError('Empty text')

    doc.doc_source = content
    doc.stripped = stripped
    doc.meta = meta
    """
    except BaseException as err:
        if type(err) == HTTPError:
            #print(url, err.code)
            logging.error("Ошибка загрузки код: " + str(err.code) + " url: " + url)
        else:
            #print(url, type(err))
            logging.error("Ошибка загрузки тип: " + type(err) + " url: " + url)
        document = Document(doc_id=doc_id, status=failed_status)
        update(document)
    """



    # wks.insert_row([url,json_obj["title"],readable_title,readable_stripped,stripped], 1)
    #exit()


if __name__ == '__main__':

    #scope = ['https://spreadsheets.google.com/feeds']
    #credentials = ServiceAccountCredentials.from_json_keyfile_name('gspreadauth.json', scope)
    #gc = gspread.authorize(credentials)
    #wks = gc.open_by_key('1jE_kKLC0us74INWi26Pw3Jh1EsvFaHqYZmcYkfAzdgY').sheet1


    articles = select(Document.doc_id, Document.source_id == '71dc5343-c27d-44bf-aa76-f4d8085317fe').fetchall()
    print(len(articles))
    from mprorp.controller.logic import SITE_PAGE_COMPLETE_STATUS, SITE_PAGE_LOADING_FAILED
    #articles = select(Document.doc_id, Document.guid == 'http://u-news24.com/archives/18306').fetchall()
    for article_id in articles:
        find_full_text(article_id[0], SITE_PAGE_COMPLETE_STATUS, SITE_PAGE_LOADING_FAILED)
    #print(articles)
    # delete("documents",Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8')
    # print(len(select(Document.created, Document.source_id == 'f4cb43e4-31bb-4d34-9367-66152e63daa8').fetchall()))
