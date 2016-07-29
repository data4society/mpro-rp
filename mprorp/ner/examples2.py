import mprorp.ner.NER as NER
import os
import mprorp.db.dbDriver as Driver
from mprorp.db.models import Document
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.tomita.tomita_run import run_tomita2
import mprorp.ner.feature as ner_feature
from mprorp.ner.identification import create_answers_feature_for_doc_2
from mprorp.ner.identification import create_markup

# 1. Create sets: training and dev
# docs = db.get_docs_with_markup('30')
# train_num = round(len(docs) * 0.8)
# print(db.put_training_set(docs[:train_num]))
# print(db.put_training_set(docs[train_num:len(docs)]))

training_set = u'1fe7391a-c5b9-4a07-bb6a-e6e4c5211008'
dev_set = u'97106298-d85e-4602-803f-a3c54685ada6'

# 2. morpho and other steps for docs from sets
# for set_doc in [training_set, dev_set]:
#     for doc_id in db.get_set_docs(set_doc):
#         rb.morpho_doc2(str(doc_id))
#         rb.lemmas_freq_doc2(str(doc_id))
#         for gram in grammar_config:
#             run_tomita2(gram, str(doc_id))
#             ner_feature.create_tomita_feature2(str(doc_id), grammar_config.keys())
#         ner_feature.create_embedding_feature2(str(doc_id))
#         ner_feature.create_morpho_feature2(str(doc_id))

# 3. Create answers for docs
# for set_doc in [training_set, dev_set]:
#     for doc_id in db.get_set_docs(set_doc):
#         create_answers_feature_for_doc_2(doc_id)

# 4. NER Learning

# NER.NER_person_learning()

# 5. NER + identification
doc_id = u'dd5454b6-70a7-4963-894d-1c4b89e6dab6'
session = Driver.db_session()
doc = session.query(Document).filter_by(doc_id=doc_id).first()
#
# settings = [['./weights/ner_oc1.params', './weights/ner_oc1.weights'],
#             ['./weights/ner_oc2.params', './weights/ner_oc2.weights']]
#
# NER.NER_predict(doc, settings, session)
#
create_markup(doc)

