import mprorp.ner.NER_learning as NER
import os
import mprorp.db.dbDriver as Driver
from mprorp.db.models import Document

if not os.path.exists("./weights"):
    os.makedirs("./weights")

filename_tf = './weights/ner.weights'
filename_params = './weights/ner.params'

NER.NER_learning(filename_params, filename_tf)

doc_id = u'1e9ffd80-a2c2-8432-1c36-6205737998d5'
session = Driver.db_session()
doc = session.query(Document).filter_by(doc_id=doc_id).first()

NER.NER_predict(doc, session, filename_params, filename_tf)