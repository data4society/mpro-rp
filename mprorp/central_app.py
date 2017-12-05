"""start script for celery based running"""
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import sys
sys.path.append('..')
import traceback
from celery import Celery
import mprorp.config.celeryconfig as celeryconfig
from mprorp.controller.init import *
import logging

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', filename = u'/home/mprorp/mpro-rp-dev/cel.txt')
root = logging.getLogger()
root.setLevel(logging.DEBUG)

logging.info("start init")
app = Celery('mprorp')
app.config_from_object(celeryconfig)
logging.info("fin init")


flask_app = Flask(__name__)
CORS(flask_app)

import os

app = Celery('mprorp',
                 broker=os.environ['CELERYD_BROKER_URL'],
                 backend='rpc',
                 )
if worker:
    import mprorp.config.celeryconfig as celeryconfig
    app.config_from_object(celeryconfig)


@flask_app.route('/api/last_docs/<status>/<date>/<sql_query>', methods=['GET'])
def get_last_docs(status, date, sql_query):
    """get list of docs created after date"""
    try:
        session = db_session()
        docs = session.query(Document).filter_by(status=status).filter(Document.created > date) \
            .filter(Document.tsv.match(sql_query, postgresql_regconfig='russian')).all()
        session.remove()
        response = []
        for doc in docs:
            doc_dict = doc.__dict__
            doc_dict.pop('_sa_instance_state')
            doc_dict.pop('tsv')
            doc_dict.pop('doc_id')
            doc_dict.pop('app_id')
            doc_dict.source_with_type = "central " + doc_dict.source_with_type
            response.append(doc_dict)
        out_json = {"status": "OK", "response": response}
    except Exception as err:
        err_txt = traceback.format_exc()
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    return jsonify(out_json)

if flask_instance and __name__ == 'central_app':
    from werkzeug.contrib.fixers import ProxyFix
    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app)
    from mprorp.db.dbDriver import *
    from mprorp.db.models import *
    from sqlalchemy.orm.attributes import flag_modified
    #flask_app.run(port=8000,debug=False)
