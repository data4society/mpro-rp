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
import mprorp.controller.logic as logic
from mprorp.celery_app import load_app_conf
from mprorp.crawler.site_page import find_full_text
from mprorp.config.settings import *
from mprorp.utils import relative_file_path
from readability.htmls import build_doc


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
    sheets_by_titles = {}
    for sheet in sheets:
        sheets_by_titles[sheet.title] = sheet
    for app_id in records:
        record = records[app_id]
        if app_id in sheets_by_titles:
            sheet = sheets_by_titles[app_id]
            head_row = sheet.row_values(1)
        else:
            sheet = spreadsheet.add_worksheet(app_id, 1, 1)
            head_row = ['time']
            sheet.update_cell(1, 1, 'time')
        print(head_row)
        for key in record:
            if key not in head_row:
                head_row.append(key)
                sheet.add_cols(1)
                sheet.update_cell(1, len(head_row), key)
        new_row = []
        for key in head_row:
            if key in record:
                if type(record[key]) == 'datetime.datetime':
                    new_row.append(-1)
                else:
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

    records = {}
    base_record = {}
    base_record['time'] = str(datetime.datetime.now())[0:19]
    base_record['commiters'] = '\n'.join(commiters)
    base_record['comments'] = '\n'.join(comments)
    #record['compare'] = 'https://api.github.com/repos/data4society/mpro-rp/git/refs/heads/dev'
    base_record['compare'] = 'https://github.com/data4society/mpro-rp/compare/'+commit_range
    base_record['commit_range'] = commit_range
    credentials_dict = {
        "type": "service_account",
        "private_key_id": google_private_key_id,
        "private_key": google_private_key,
        "client_email": google_client_email,
        "client_id": google_client_id
    }

    #dropall_and_create()
    with open(relative_file_path(__file__, '../mprorp/tests/test_docs/time_test.html'), 'r') as f:
        text = f.read()
    apps_config = variable_get(cur_app_config)
    test_guid = 'time_test_guid'
    for app_id in apps_config:
        app_conf = apps_config[app_id]
        if "time_test" in app_conf:
            print("APPID: "+app_id)
            time = datetime.datetime.now()
            session = db_session()
            old_doc = session.query(Document).filter_by(guid=test_guid).first()
            if old_doc:
                delete_document(str(old_doc.doc_id))
            new_doc = Document(guid=test_guid, app_id=app_id, url='http://test.com/test', status=logic.SITE_PAGE_READABILITY_COMPLETE_STATUS, type='article')
            new_doc.published_date = datetime.datetime.now()
            meta = dict()
            meta["publisher"] = {"name": 'test'}
            #meta["abstract"] = desc
            new_doc.meta = meta
            encoding = 'utf-8'
            new_doc.doc_source = encoding + "|||" + text
            find_full_text(new_doc, session, None)
            session.add(new_doc)
            session.commit()
            app_record = base_record.copy()
            app_record['readability'] = (datetime.datetime.now() - time).total_seconds()
            logic.logic_times = {'total': 0}
            logic.router(new_doc.doc_id, app_id, logic.SITE_PAGE_READABILITY_COMPLETE_STATUS)
            app_record.update(logic.logic_times)
            app_record['config'] = app_conf
            app_record['total'] = app_record['total']+app_record['readability']
            delete_document(str(new_doc.doc_id))
            records[app_id] = app_record
    print(records)
    write_to_spreadsheet(credentials_dict, google_spreadsheet_id, records)

    print("FINISH TIMING")
