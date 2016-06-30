"""vkontakte list and item parser"""
from mprorp.celery_app import app
from mprorp.controller.logic import *

from mprorp.db.dbDriver import *
from mprorp.db.models import *

from requests import Request, Session
import json
import datetime
from mprorp.crawler.utils import *

#import logging
#logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG)

def send_get_request(url):
    """accessory function for sending requests"""
    s = Session()
    req = Request('GET', url)
    prepped = req.prepare()
    r = s.send(prepped)
    r.encoding = 'utf-8'
    return r.text

@app.task
def vk_start_parsing(source_id):
    print('vk_start_parsing')
    """download vk response and run list parsing function"""
    # get source url
    [source_url, parse_period] = select([Source.url,Source.parse_period], Source.source_id == source_id).fetchone()
    # download vk response
    req_result = send_get_request(source_url)
    # run list parsing function
    vk_parse_list(req_result, source_id)
    # change next timestamp crawl start
    next_crawling_time = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + parse_period)
    source = Source(source_id = source_id, next_crawling_time = next_crawling_time, wait = True)
    update(source)
    print("VK CRAWL COMPLETE")


def vk_parse_list(req_result, source_id):
    """parses one source, get list and do initial insert"""

    # convert to json object
    json_obj = json.loads(req_result)
    for item in json_obj["response"]:
        if type(item) == dict:  # vk api can give Integer (Number of posts?) at the same level
            post_type = item["post_type"]
            if post_type == 'reply':
                url = 'https://vk.com/wall' + str(item["owner_id"]) + '_'+str(item["post_id"])+'?reply='+str(item["id"])
            elif post_type == 'post' or post_type == 'copy':
                url = 'https://vk.com/wall' + str(item["owner_id"]) + '_' + str(item["id"])
            else:
                raise ValueError('Unknown post type: '+post_type)

            # Skip item if we have any row in Document table with same guid (url)
            # skip all not 'post' items
            if post_type == 'post' and not select(Document.doc_id, Document.guid == url).fetchone():
                # initial insert with guid start status and reference to source
                new_doc = Document(guid=url, source_id=source_id, status=0, type='vk')
                insert(new_doc)
                # further parsing
                new_doc_id = new_doc.doc_id
                vk_parse_item(item, new_doc_id)
                router(new_doc_id, VK_COMPLETE_STATUS)


def vk_parse_item(item, doc_id):
    new_doc = Document(doc_id=doc_id)
    # main text
    txt = item["text"]
    stripped = strip_tags(txt)
    stripped = to_plain_text(stripped)
    new_doc.doc_source = txt
    new_doc.stripped = stripped
    # publish date timestamp
    timestamp = item["date"]
    new_doc.published_date = datetime.datetime.fromtimestamp(timestamp)

    # additional information
    meta_json = dict()
    # post type ('post', 'copy' or 'reply')
    post_type = item["post_type"]
    meta_json['vk_post_type'] = post_type
    # full attachments info
    if "attachments" in item:
        attachments = item["attachments"]
        meta_json['vk_attachments'] = attachments
    # owner info
    meta_json['vk_owner'] = vk_get_user(item["owner_id"])
    new_doc.meta = meta_json # json.dumps(meta_json)

    new_doc.status = 1  # this status mean complete crawler work with this item
    # update row in database
    update(new_doc)


def vk_get_user(owner_id):
    """get user or page that owns post"""
    if owner_id > 0:
        req_result = send_get_request('https://api.vk.com/method/users.get?user_ids='+str(owner_id))
        json_obj = json.loads(req_result)
        json_obj = json_obj["response"][0]
        json_obj["owner_type"] = "user"
        json_obj["owner_url"] = "https://vk.com/id"+str(owner_id)
    else:
        req_result = send_get_request('https://api.vk.com/method/groups.getById?group_ids=' + str(-owner_id))
        json_obj = json.loads(req_result)
        json_obj = json_obj["response"][0]
        json_obj["owner_type"] = "group"
        json_obj["owner_url"] = "https://vk.com/club"+str(-owner_id)
    return json_obj


if __name__ == '__main__':
    # delete("documents",Document.source_id == '2c00848d-dc19-4de0-a076-8d89c414a4fd')
    vk_start_parsing('2c00848d-dc19-4de0-a076-8d89c414a4fd')
    # print(len(select(Document.created, Document.source_id == '2c00848d-dc19-4de0-a076-8d89c414a4fd').fetchall()))

