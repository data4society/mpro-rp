"""start script for celery based running"""
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import sys
sys.path.append('..')
import traceback
from celery import Celery
from mprorp.controller.init import *
from mprorp.crawler.utils import domain_from_path
import logging

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', filename = u'/home/mprorp/mpro-rp-dev/cel.txt')
root = logging.getLogger()
root.setLevel(logging.DEBUG)


flask_app = Flask(__name__)
CORS(flask_app)

import os

if worker:
    logging.info("start init")
    app = Celery('mprorp',
                 broker=os.environ['CELERYD_BROKER_URL'],
                 backend='rpc',
                 )
    import mprorp.config.celeryconfig as celeryconfig
    app.config_from_object(celeryconfig)
    logging.info("fin init")


@flask_app.route('/api/test', methods=['GET'])
def test():
    try:
        out_json = {"status": "OK"}
    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    return jsonify(out_json)


@flask_app.route('/api/last_docs', methods=['POST'])
def get_last_docs():
    """get list of docs created after date"""
    try:
        app_id = "central"
        status = "105"
        in_json = request.json
        sql_query = in_json["sql_query"]
        black_list = in_json["black_list"]
        date = in_json["date"]

        session = db_session()
        docs = session.query(Document).filter_by(status=status).filter_by(app_id=app_id).filter(Document.created > date) \
            .filter(Document.tsv.match(sql_query, postgresql_regconfig='russian')).all()
        #select * from documents where status=105 and app_id='central' and created>'2018-04-17 02:00:00.107869' and
        session.remove()
        response = []
        for doc in docs:
            if domain_from_path(doc.url) not in black_list:
                doc.source_with_type = "central " + doc.source_with_type
                doc_dict = doc.__dict__
                doc_dict.pop('_sa_instance_state')
                doc_dict.pop('tsv')
                doc_dict.pop('app_id')
                doc_dict['created'] = str(doc_dict['created'])
                doc_dict['published_date'] = str(doc_dict['published_date'])
                response.append(doc_dict)
        out_json = {"status": "OK", "response": response}
    except Exception as err:
        err_txt = traceback.format_exc()
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    logging.info("FIN LAST DOCS2")
    return jsonify(out_json)

if flask_instance and __name__ == 'central_app':
    from werkzeug.contrib.fixers import ProxyFix
    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app)
    from mprorp.db.dbDriver import *
    from mprorp.db.models import *
    from sqlalchemy.orm.attributes import flag_modified
    #flask_app.run(port=8000,debug=False)
