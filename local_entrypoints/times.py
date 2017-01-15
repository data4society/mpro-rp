"""get procedures times and write them"""
import sys
import os
import json
import datetime
import gspread
import json
sys.path.insert(0, '..')
from mprorp.db.models import *
from mprorp.crawler.utils import *
from oauth2client.service_account import ServiceAccountCredentials
from mprorp.controller.logic import *
from mprorp.utils import home_dir
from mprorp.crawler.readability.readability2 import find_full_text
from mprorp.celery_app import load_app_conf
from mprorp.crawler.site_page import readability_and_meta


def write_to_spreadsheet(credentials_dict, spreadsheet_id, record):
    # authorization: http://gspread.readthedocs.io/en/latest/oauth2.html
    scope = ['https://spreadsheets.google.com/feeds']
    #credentials = ServiceAccountCredentials.from_json_keyfile_name('keyfile.json', scope)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    gc = gspread.authorize(credentials)

    print("authorization OK")
    wks = gc.open_by_key(spreadsheet_id).sheet1
    print("spreadsheet open OK")
    head_row = wks.row_values(1)
    print(head_row)
    for key in record:
        if key not in head_row:
            head_row.append(key)
            wks.add_cols(1)
            wks.update_cell(1, len(head_row), key)
    new_row = []
    for key in head_row:
        if key in record:
            new_row.append(record[key])
        else:
            new_row.append('')
    wks.append_row(new_row)

if __name__ == '__main__':
    print("START TIMING")
    #print(os.environ['TRAVIS_COMMIT_RANGE'])
    #print(os.environ['MY_PASSWORD'])
    cur_app_config = 'test_config'
    commit_range = os.environ['TRAVIS_COMMIT_RANGE']
    private_key_id = os.environ['GOOGLE_PRIVATE_KEY_ID']
    private_key = os.environ['GOOGLE_PRIVATE_KEY']
    client_email = os.environ['GOOGLE_CLIENT_EMAIL']
    client_id = os.environ['GOOGLE_CLIENT_ID']
    spreadsheet_id = os.environ['SPREADSHEET_ID']

    url = 'https://api.github.com/repos/data4society/mpro-rp/compare/'+commit_range
    req_result = send_get_request(url, gen_useragent=True)
    json_obj = json.loads(req_result)
    commits = json_obj["commits"]
    #links = []
    comments = []
    commiters = []
    for commit in commits:
        #links.append(commit['html_url'])
        comments.append(commit['commit']['message'])
        commiters.append(commit['author']['login'])

    print(comments)
    record = {}
    record['time'] = str(datetime.datetime.now())[0:19]
    record['commiters'] = '\n'.join(commiters)
    record['comments'] = '\n'.join(comments)
    #record['compare'] = 'https://api.github.com/repos/data4society/mpro-rp/git/refs/heads/dev'
    record['compare'] = 'https://github.com/data4society/mpro-rp/compare/'+commit_range
    credentials_dict = {
        "type": "service_account",
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id
    }

    #dropall_and_create()
    print("load_app_conf")
    load_app_conf('config/app.time.json', cur_app_config)
    print("load_app_conf1")
    with open(relative_file_path(__file__, '../mprorp/tests/test_docs/time_test.html'), 'rb') as f:
        text = f.read()
    time = datetime.datetime.now()
    app_id = 'test_time'
    new_doc = Document(guid='test_guid', app_id=app_id, url='http://test.com/test', status=SITE_PAGE_COMPLETE_STATUS, type='article')
    session = db_session()
    new_doc.published_date = datetime.datetime.now()
    meta = dict()
    meta["publisher"] = {"name": 'test'}
    #meta["abstract"] = desc
    new_doc.meta = meta
    readability_and_meta(new_doc, session, text)
    session.add(new_doc)
    session.commit()
    record['readability'] = (datetime.datetime.now() - time).total_seconds()
    router(new_doc.doc_id, app_id, SITE_PAGE_COMPLETE_STATUS)
    record.update(logic_times)
    print("write_to_spreadsheet")
    delete_app_documents(app_id)
    write_to_spreadsheet(credentials_dict, spreadsheet_id, record)

    print("FINISH TIMING")
