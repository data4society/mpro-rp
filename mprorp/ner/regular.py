from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup
from mprorp.celery_app import app

from mprorp.db.dbDriver import *
from mprorp.db.models import *

import mprorp.ner.feature as ner_feature


@app.task
def regular_entities(doc_id):
    convert_tomita_result_to_markup(doc_id, ['person.cxx'])
    doc = Document(doc_id=doc_id, status=1000)
    update(doc)


def regular_tomita_features(doc_id):
    ner_feature.create_tomita_features(doc_id, ['date.cxx', 'person.cxx'], 50)
