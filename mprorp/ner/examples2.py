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

if not os.path.exists("./weights"):
    os.makedirs("./weights")

NER_config = NER.Config()
# NER_config.training_set = training_set
# NER_config.dev_set = dev_set
#
# NER_config.feature_answer = ['oc_feature_last_name', 'oc_feature_first_name', 'oc_feature_middle_name',
#                              'oc_feature_nickname', 'oc_feature_foreign_name']
#
# filename_tf = './weights/ner_oc1.weights'
# filename_params = './weights/ner_oc1.params'
#
# NER.NER_learning(filename_params, filename_tf, NER_config)
#
# NER_config.feature_answer = ['oc_feature_post', 'oc_feature_role', 'oc_feature_status']
#
# filename_tf = './weights/ner_oc2.weights'
# filename_params = './weights/ner_oc2.params'
#
# NER.NER_learning(filename_params, filename_tf, NER_config)

# 5. NER + identification
# doc_id = u'1e9ffd80-a2c2-8432-1c36-6205737998d5'
# session = Driver.db_session()
# doc = session.query(Document).filter_by(doc_id=doc_id).first()
#
# settings = [['./weights/ner_oc1.params', './weights/ner_oc1.weights'],
#             ['./weights/ner_oc2.params', './weights/ner_oc2.weights']]
#
# NER.NER_predict(doc, settings, session)
#
# create_markup(doc)

NER.NER_person_learning()