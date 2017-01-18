"""get procedures times and write them"""
import sys
import os
import datetime
import gspread
import json
sys.path.insert(0, '..')
from mprorp.db.models import *
from mprorp.db.dbDriver import *
from mprorp.crawler.utils import *
from oauth2client.service_account import ServiceAccountCredentials
from mprorp.controller.logic import *
from mprorp.celery_app import load_app_conf
from mprorp.crawler.site_page import readability_and_meta
from mprorp.config.settings import *


def write_to_spreadsheet(credentials_dict, spreadsheet_id, records):
    # authorization: http://gspread.readthedocs.io/en/latest/oauth2.html
    scope = ['https://spreadsheets.google.com/feeds']
    #credentials = ServiceAccountCredentials.from_json_keyfile_name('keyfile.json', scope)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    gc = gspread.authorize(credentials)

    print("authorization OK")
    spreadsheet = gc.open_by_key(spreadsheet_id)
    print("spreadsheet open OK")
    sheets = spreadsheet.worksheets()
    print(sheets)
    print(type(sheets[0]))
    for app_id in records:
        record = records[app_id]
        if app_id in sheets:
            sheet = spreadsheet.worksheet(app_id)
        else:
            sheet = spreadsheet.add_worksheet(app_id, 1, 0)
        head_row = sheet.row_values(1)
        print(head_row)
        for key in record:
            if key not in head_row:
                head_row.append(key)
                sheet.add_cols(1)
                sheet.update_cell(1, len(head_row), key)
        new_row = []
        for key in head_row:
            if key in record:
                new_row.append(record[key])
            else:
                new_row.append('')
        sheet.append_row(new_row)

if __name__ == '__main__':
    print("START TIMING")
    #print(os.environ['TRAVIS_COMMIT_RANGE'])
    #print(os.environ['MY_PASSWORD'])
    cur_app_config = 'test_config'
    if 'TRAVIS_COMMIT_RANGE' in os.environ:
        commit_range = os.environ['TRAVIS_COMMIT_RANGE']
        google_private_key_id = os.environ['GOOGLE_PRIVATE_KEY_ID']
        google_private_key = os.environ['GOOGLE_PRIVATE_KEY']
        google_client_email = os.environ['GOOGLE_CLIENT_EMAIL']
        google_client_id = os.environ['GOOGLE_CLIENT_ID']
        google_spreadsheet_id = os.environ['SPREADSHEET_ID']
        load_app_conf('config/app.time.json', cur_app_config)
    else:
        url = 'https://api.github.com/repos/data4society/mpro-rp/git/refs/heads/dev'
        req_result = send_get_request(url, gen_useragent=True)
        json_obj = json.loads(req_result)
        last_commit = json_obj["object"]["sha"][0:7]
        commit_range = variable_get('commit_range', last_commit+"..."+last_commit)
        commit_range_list = commit_range.split("...")
        if last_commit != commit_range[1]:
            commit_range_list[0] = commit_range_list[1]
            commit_range_list[1] = last_commit
            commit_range = "...".join(commit_range_list)
            variable_set('commit_range', commit_range)
        load_app_conf('config/app.json', cur_app_config)
    print(commit_range)
    url = 'https://api.github.com/repos/data4society/mpro-rp/compare/'+commit_range
    req_result = send_get_request(url, gen_useragent=True)
    json_obj = json.loads(req_result)
    commits = json_obj["commits"]
    if len(commits) == 0:
        commits = [json_obj["base_commit"]]
    #links = []
    comments = []
    commiters = []
    for commit in commits:
        #links.append(commit['html_url'])
        comments.append(commit['commit']['message'])
        commiters.append(commit['commit']['committer']['name'])

    print(comments)
    records = {}
    base_record = {}
    base_record['time'] = str(datetime.datetime.now())[0:19]
    base_record['commiters'] = '\n'.join(commiters)
    base_record['comments'] = '\n'.join(comments)
    #record['compare'] = 'https://api.github.com/repos/data4society/mpro-rp/git/refs/heads/dev'
    base_record['compare'] = 'https://github.com/data4society/mpro-rp/compare/'+commit_range
    credentials_dict = {
        "type": "service_account",
        "private_key_id": google_private_key_id,
        "private_key": google_private_key,
        "client_email": google_client_email,
        "client_id": google_client_id
    }

    #dropall_and_create()
    with open(relative_file_path(__file__, '../mprorp/tests/test_docs/time_test.html'), 'rb') as f:
        text = f.read()
    apps_config = variable_get(cur_app_config)
    for app_id in apps_config:
        app_conf = apps_config[app_id]
        if "time_test" in app_conf:
            time = datetime.datetime.now()
            new_doc = Document(guid='time_test_guid', app_id=app_id, url='http://test.com/test', status=SITE_PAGE_COMPLETE_STATUS, type='article')
            session = db_session()
            new_doc.published_date = datetime.datetime.now()
            meta = dict()
            meta["publisher"] = {"name": 'test'}
            #meta["abstract"] = desc
            new_doc.meta = meta
            readability_and_meta(new_doc, session, text)
            session.add(new_doc)
            session.commit()
            app_record = base_record.copy()
            app_record['readability'] = (datetime.datetime.now() - time).total_seconds()
            router(new_doc.doc_id, app_id, SITE_PAGE_COMPLETE_STATUS)
            app_record.update(logic_times)
            app_record['config'] = str(app_conf)
            print("write_to_spreadsheet")
            delete_document(str(new_doc.doc_id))
            records[app_id] = app_record
    write_to_spreadsheet(credentials_dict, google_spreadsheet_id, records)

    print("FINISH TIMING")
