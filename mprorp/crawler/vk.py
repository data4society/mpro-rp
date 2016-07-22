"""vkontakte list and item parser"""

from mprorp.db.models import *

import json
import datetime
from mprorp.crawler.utils import *

#import logging
#logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.DEBUG)


def vk_start_parsing(source_id, session):
    """download vk response and run list parsing function"""
    # get source object
    source = session.query(Source).filter_by(source_id=source_id).first()
    print('vk start parsing source:' + source.name)
    # download vk response
    req_result = send_get_request(source.url)
    # run list parsing function
    docs = vk_parse_list(req_result, source_id, session)
    # change next timestamp crawl start
    source.next_crawling_time = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + source.parse_period)
    source.wait = True
    print("VK CRAWL COMPLETE")
    return docs


def vk_parse_list(req_result, source_id, session):
    """parses one source, get list and do initial insert"""

    # convert to json object
    json_obj = json.loads(req_result)
    docs = []
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
            if post_type == 'post' and session.query(Document).filter_by(guid=url).count() == 0:
                # initial insert with guid start status and reference to source
                new_doc = Document(guid=url, source_id=source_id, status=0, type='vk')
                docs.append(new_doc)
                # further parsing
                vk_parse_item(item, new_doc, session)
    return docs


def vk_parse_item(item, new_doc, session):
    # main text
    txt = item["text"]
    stripped = strip_tags('<html><body>' + txt + '</body></html>')
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

    #.status = VK_COMPLETE_STATUS  # this status mean complete crawler work with this item

    session.add(new_doc)
    #router(doc_id, VK_COMPLETE_STATUS)


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

