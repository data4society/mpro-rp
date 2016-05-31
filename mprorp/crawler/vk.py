"""vkontakte list and item parser"""
from requests import Request, Session
import json
import datetime

from mprorp.db.dbDriver import *
from mprorp.db.models import *


def send_get_request(url):
    """accessory function for sending requests"""
    s = Session()
    req = Request('GET', url)
    prepped = req.prepare()
    r = s.send(prepped)
    r.encoding = 'utf-8'
    return r.text


def vk_start_parsing(source_id):
    """download vk response and run list parsing function"""
    # get source url
    source_url = select(Source.url, Source.source_id == source_id).fetchone()[0]
    # download vk response
    req_result = send_get_request(source_url)
    # run list parsing function
    vk_parse_list(req_result, source_id)


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
                new_doc = Document(guid=url, source_ref=source_id, status=0)
                insert(new_doc)
                # further parsing
                vk_parse_item(item, new_doc.doc_id)


def vk_parse_item(item, doc_id):
    new_doc = Document(doc_id=doc_id)
    # main text
    txt = item["text"]
    new_doc.doc_source = txt
    new_doc.stripped = txt
    # publish date timestamp
    timestamp = item["date"]
    new_doc.created = datetime.datetime.fromtimestamp(timestamp)

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
    new_doc.meta = json.dumps(meta_json)

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
    #delete("document",Document.source_ref == 'd1fb37ef-1808-45f6-9234-5ed2969e920a')
    vk_start_parsing('d1fb37ef-1808-45f6-9234-5ed2969e920a')
    # print(len(select(Document.issue_date, Document.source_ref == 'd1fb37ef-1808-45f6-9234-5ed2969e920a').fetchall()))

