"""flask HTTP client for fastart"""
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import sys
sys.path.append('../..')
import traceback
from celery import Celery

from mprorp.controller.init import *
import logging

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', filename = u'/home/mprorp/mpro-rp-dev/fastart.txt')
root = logging.getLogger()
root.setLevel(logging.DEBUG)
#logging.info(sys.argv)


flask_app = Flask(__name__)
CORS(flask_app)

cel_app = Celery('mprorp', backend='rpc')
if worker == 'fastart':
    import mprorp.config.fastart_celeryconfig as celeryconfig
    cel_app.config_from_object(celeryconfig)


@flask_app.route('/rubrics', methods=['GET'])
def get_all_rubrics():
    """get list of fastart rubrics with names and current statuses"""
    try:
        session = db_session()
        rubrics = session.query(FastartRubric.rubric_id,FastartRubric.name,FastartRubric.step,FastartRubric.doc_ind).all()
        session.close()
        response = []
        for rubric in rubrics:
            if rubric.step == -1:
                status = "Complete"
            elif rubric.doc_ind == -1:
                status = "Learning"
            else:
                status = "Marking"
            response.append({"rubric_id":rubric.rubric_id,"name":rubric.name,"status":status})
        out_json = {"status":"OK","response":response}
    except Exception as err:
        err_txt = traceback.format_exc()
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    return jsonify(out_json)


@flask_app.route('/rubrics', methods=['POST'])
def create_rubric():
    """create new rubric if there is enough docs by query"""
    try:
        in_json = request.json
        query = in_json["query"]
        sql_query = to_sql_query(query)
        session = db_session()
        search_result, doc_num = search(sql_query, session)
        if search_result:
            docs = session.query(Document.doc_id).filter_by(app_id='mediametrics').filter_by(status=1000).filter(Document.tsv.match(sql_query, postgresql_regconfig='russian')).limit(DOCS_MIN_NUM)
            docs = [{"doc_id":str(doc[0]),"answer":-1} for doc in docs]
            rubric = FastartRubric(name=in_json["name"],desc=in_json["desc"],query=query,sql_query=sql_query,docs={"all":docs})
            session.add(rubric)
            session.commit()
            response = {"rubric_id":rubric.rubric_id,"doc_num":doc_num}
            out_json = {"status":"OK","response":response}
        else:
            out_json = {"status":"Error","code":"Not enough docs","doc_num":doc_num}
        session.close()
    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    return jsonify(out_json)


@flask_app.route('/rubrics/<rubric_id>', methods=['GET'])
def get_rubric(rubric_id):
    abort_num = 0
    try:
        session = db_session()
        rubric = session.query(FastartRubric).filter_by(rubric_id = rubric_id).first()
        if rubric:
            docs = rubric.docs
            all = docs["all"]
            step = rubric.step
            #logging.info("step: "+str(step)+" len docs: "+str(len(all)))
            if step != -1:
                doc_ind = rubric.doc_ind
                #logging.info("doc_ind: "+str(doc_ind)+" step: "+str(step)+" len docs: "+str(len(all)))
                if doc_ind != -1:
                    good_ans = step*3+1
                    bad_ans = step*3+2
                    #skip_ans = step*3
                    good_num = len([1 for doc in all if doc["answer"]==good_ans])
                    bad_num = len([1 for doc in all if doc["answer"]==bad_ans])
                    #skip_num = len([1 for doc in all if doc["answer"]==skip_ans])
                    response = {"name": rubric.name, "desc": rubric.desc,"query":rubric.query,"step":step,"good_remaining":GOOD_MIN_NUM-good_num,"bad_remaining":BAD_MIN_NUM-bad_num,"doc":get_doc(all[doc_ind]["doc_id"],session)}
                    out_json = {"status": "OK","response": response}
                else:
                    response = {"name":rubric.name, "desc": rubric.desc, "step": step}
                    out_json = {"status": "Learning", "response": response}
            else:
                response = {"name": rubric.name, "desc": rubric.desc, "step": step, "model_name": rubric.models['model_name']}
                out_json = {"status": "Complete", "response": response}
        else:
            abort_num = 404
        session.close()
    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    if abort_num:
        abort(abort_num)
    return jsonify(out_json)


@flask_app.route('/rubrics/<rubric_id>', methods=['DELETE'])
def delete_rubric(rubric_id):
    abort_num = 0
    try:
        session = db_session()
        result = session.query(FastartRubric).filter_by(rubric_id = rubric_id).delete()
        session.commit()
        session.close()
        if result:
            out_json = {"status":"OK"}
        else:
            abort_num = 404
    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    if abort_num:
        abort(abort_num)
    return jsonify(out_json)


@flask_app.route('/rubrics/<rubric_id>', methods=['PUT'])
def update_rubric(rubric_id):
    abort_num = 0
    try:
        in_json = request.json
        session = db_session()
        rubric = session.query(FastartRubric).filter_by(rubric_id = rubric_id).first()
        if rubric:
            if "name" in in_json:
                rubric.name = in_json["name"]
            if "desc" in in_json:
                rubric.desc = in_json["desc"]
            if "query" in in_json:
                query = in_json["query"]
                sql_query = to_sql_query(query)
                rubric.query = query
                rubric.sql_query = sql_query
            session.commit()
            out_json = {"status":"OK"}
        else:
            abort_num = 404
        session.close()
    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    if abort_num:
        abort(abort_num)
    return jsonify(out_json)



@flask_app.route('/rubrics/<rubric_id>/answer', methods=['POST'])
def set_answer(rubric_id):
    abort_num = 0
    try:
        in_json = request.json
        session = db_session()
        rubric = session.query(FastartRubric).filter_by(rubric_id = rubric_id).first()
        if rubric:
            step = rubric.step
            if step != -1:
                doc_ind = rubric.doc_ind
                if doc_ind != -1:
                    docs = rubric.docs
                    all = docs["all"]
                    good_ans = step*3+1
                    bad_ans = step*3+2
                    skip_ans = step*3
                    answer = in_json["answer"]
                    if all[doc_ind]["doc_id"] == in_json["doc_id"]:
                        all[doc_ind]["answer"] = answer+step*3
                        good_num = len([1 for doc in all if doc["answer"]==good_ans])
                        bad_num = len([1 for doc in all if doc["answer"]==bad_ans])
                        skip_num = len([1 for doc in all if doc["answer"]==skip_ans])
                        flag_modified(rubric, "docs")

                        if good_num >= GOOD_MIN_NUM and bad_num >= BAD_MIN_NUM:
                            rubric.doc_ind = -1
                            session.commit()
                            create_model.delay(rubric_id)
                        else:
                            rubric.doc_ind += 1
                            session.commit()
                            #response = {"good_num":good_num,"bad_num":bad_num,"doc":get_doc(all[rubric.doc_ind].doc_id,session)}
                        out_json = {"status":"OK"}
                    else:
                        out_json = {"status":"Error","text":"wrong doc"}
                else:
                    out_json = {"status":"Error","text":"learning now"}
            else:
                out_json = {"status":"Error","text":"rubric complete"}
        else:
            abort_num = 404
        session.close()

    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    if abort_num:
        abort(abort_num)
    return jsonify(out_json)


@flask_app.route('/rubrics/<rubric_id>/fulltext', methods=['GET'])
def get_fulltext(rubric_id):
    abort_num = 0
    try:
        session = db_session()
        rubric = session.query(FastartRubric).filter_by(rubric_id = rubric_id).first()
        if rubric:
            step = rubric.step
            if step != -1:
                doc_ind = rubric.doc_ind
                if doc_ind != -1:
                    docs = rubric.docs
                    all = docs["all"]
                    stripped = session.query(Document.stripped).filter_by(doc_id = all[doc_ind]["doc_id"]).first()[0]
                    out_json = {"status":"OK","response":stripped}
                else:
                    response = {"name":rubric.name,"desc":rubric.desc,"step":step}
                    out_json = {"status":"Learning","response":response}
            else:
                response = {"name":rubric.name,"desc":rubric.desc,"step":step}
                out_json = {"status":"Error","text":"rubric complete"}
        else:
            abort_num = 404
        session.close()

    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    if abort_num:
        abort(abort_num)
    return jsonify(out_json)







@flask_app.route('/rubrics/<rubric_id>/learning', methods=['GET'])
def learning(rubric_id):
    create_model.delay(rubric_id)
    return jsonify({"status":"OK"})






@flask_app.route('/rubrics/<rubric_id>/download', methods=['GET'])
def download_rubric(rubric_id):
    abort_num = 0
    try:
        session = db_session()
        rubric = session.query(FastartRubric).filter_by(rubric_id = rubric_id).first()
        if rubric:
            step = rubric.step
            if step == -1:
                response = {"name":rubric.name,"desc":rubric.desc,"model":rubric.model,"query":rubric.query,"sql_query":rubric.sql_query}
                out_json = {"status":"OK","response":response}
            else:
                out_json = {"status":"Error","text":"rubric is not complete"}
        else:
            abort_num = 404
        session.close()

    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)
        out_json = {"status":"Error"}
        out_json["text"] = "Python Server Error. "+err_txt
    if abort_num:
        abort(abort_num)
    return jsonify(out_json)


def get_doc(doc_id, session=None):
    has_session = True
    if not session:
        has_session = False
        session = db_session()
    doc = session.query(Document).filter_by(doc_id = doc_id).first()

    if not has_session:
        session.remove()
    return {"doc_id": doc_id, "abstract" :doc.stripped.split("\n")[0],"title":doc.title}


def search(sql_query, session=None):
    try:
        has_session = True
        if not session:
            has_session = False
            session = db_session()
        docs_num = session.query(Document).filter_by(app_id='mediametrics').filter_by(status=1000).filter(Document.tsv.match(sql_query, postgresql_regconfig='russian')).count()
        if not has_session:
            session.remove()
        return (docs_num>=DOCS_MIN_NUM,docs_num)
    except Exception as err:
        err_txt = traceback.format_exc()
        logging.info(err_txt)


def to_sql_query(query):
    parts = query.split(',')
    new_parts = []
    for part in parts:
        part = part.strip(' ')
        part = part.replace('_','<->')
        part = part.replace(' ','&')
        new_parts.append(part)
    sql_query = '|'.join(new_parts)
    return sql_query


if __name__ == '__main__':
    from mprorp.fastart.learning_controller import create_model
    from mprorp.db.dbDriver import *
    from mprorp.db.models import *
    from sqlalchemy.orm.attributes import flag_modified
    from mprorp.config.settings import learning_parameters as lp
    fasttext_params = lp['fasttext']
    GOOD_MIN_NUM = fasttext_params['good_min_num']
    BAD_MIN_NUM = fasttext_params['bad_min_num']
    DOCS_MIN_NUM = fasttext_params['docs_min_num']
    flask_app.run(port=8000,debug=False)