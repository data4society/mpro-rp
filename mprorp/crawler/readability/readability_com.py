"""readability.com: request to API"""
from mprorp.crawler.utils import *
import json
import html

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def find_full_text(url):
    req_url = 'https://www.readability.com/api/content/v1/parser?token=08e612cb0d3f95db2090b87d3d758efc75fb314b&url='+url
    print(req_url)
    res = send_get_request(req_url) # urllib.request.urlopen(url).read().decode('unicode-escape')# send_get_request(url).decode('unicode-escape')
    json_obj = json.loads(res)

    #print(res)

    if "error" in json_obj:
        #need logging
        return 'ERROR';
    content = json_obj["content"]
    content = html.unescape(content)
    #print(content)
    stripped = strip_tags(content)
    stripped = to_plain_text(stripped)
    return stripped

