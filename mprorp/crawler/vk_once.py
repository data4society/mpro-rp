import json
import datetime
from mprorp.crawler.utils import *

mode = "wall"  #"newsfeed"
owner_id = 294371282
count = 300
query = "тролль"


def vk_start_parsing(source_url):
    """download vk response and run list parsing function"""
    # get source object
    print('vk start parsing source:' + source_url)
    # download vk response
    req_result = send_get_request(source_url)
    # run list parsing function
    vk_parse_list(req_result)


def vk_parse_list(req_result):
    """parses one source, get list and do initial insert"""

    # convert to json object
    json_obj = json.loads(req_result)
    if not "response" in json_obj:
        print("RESPONSE ERROR")
        print(json_obj)
    for item in json_obj["response"]:
        if type(item) == dict:  # vk api can give Integer (Number of posts?) at the same level
            post_type = item["post_type"]
            if owner_id:
                owner_id0 = str(owner_id)
            else:
                owner_id0 = item["owner_id"]
            if post_type == 'reply':
                url = 'https://vk.com/wall' + owner_id0 + '_'+str(item["post_id"])+'?reply='+str(item["id"])
            elif post_type == 'post' or post_type == 'copy':
                url = 'https://vk.com/wall' + owner_id0 + '_' + str(item["id"])
            else:
                raise ValueError('Unknown post type: '+post_type)
            txt = item["text"]
            stripped = strip_tags('<html><body>' + txt + '</body></html>')
            stripped = to_plain_text(stripped)
            print(stripped)
            print(url)
            # publish date timestamp
            timestamp = item["date"]
            published_date = datetime.datetime.fromtimestamp(timestamp)

            # post type ('post', 'copy' or 'reply')
            post_type = item["post_type"]
            if "owner_id" in item:
                vk_owner = vk_get_user(item["owner_id"])


def vk_get_user(owner_id):
    """get user or page that owns post"""
    if owner_id > 0:
        req_result = send_get_request('https://api.vk.com/method/users.get?user_ids='+str(owner_id))
        json_obj = json.loads(req_result)
        if not "response" in json_obj:
            print("RESPONSE ERROR")
            print('https://api.vk.com/method/users.get?user_ids='+str(owner_id))
            print(json_obj)
        json_obj = json_obj["response"][0]
        json_obj["owner_type"] = "user"
        json_obj["owner_url"] = "https://vk.com/id"+str(owner_id)
    else:
        #print('https://api.vk.com/method/groups.getById?group_ids=' + str(-owner_id))
        req_result = send_get_request('https://api.vk.com/method/groups.getById?group_ids=' + str(-owner_id), gen_useragent=True)
        json_obj = json.loads(req_result)
        if not "response" in json_obj:
            print("RESPONSE ERROR")
            print('https://api.vk.com/method/users.get?user_ids='+str(-owner_id))
            print(json_obj)
        json_obj = json_obj["response"][0]
        json_obj["owner_type"] = "group"
        json_obj["owner_url"] = "https://vk.com/club"+str(-owner_id)
    return json_obj


if __name__ == '__main__':
    if mode == "wall":
        vk_start_parsing('https://api.vk.com/method/wall.search?count=' + str(count) + '&query=' + query + '&owner_id=' + str(owner_id))
    elif mode == "newsfeed":
        vk_start_parsing('https://api.vk.com/method/newsfeed.search?count=' + str(count) + '&q=' + query)
