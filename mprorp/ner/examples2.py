import mprorp.ner.NER as NER
import os
import mprorp.db.dbDriver as Driver
from mprorp.db.models import Document
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.tomita.tomita_run import run_tomita2
import mprorp.ner.feature as ner_feature
from mprorp.ner.identification import create_answers_feature_for_doc
from mprorp.ner.identification import create_markup
from mprorp.utils import home_dir

# 1. Create sets: training and dev
# docs = db.get_docs_with_markup('40')
# train_num = round(len(docs) * 0.8)
# print(db.put_training_set(docs[:train_num]))
# print(db.put_training_set(docs[train_num:len(docs)]))
training_set = u'9b395f00-e556-414a-a9c7-3effeb5aa7c8'
dev_set = u'4785d9ed-6435-48b5-971d-044fdfcfe678'

# 2. morpho and other steps for docs from sets
for set_doc in [training_set, dev_set]:
    for doc_id in db.get_set_docs(set_doc):
        rb.morpho_doc2(str(doc_id))
        rb.lemmas_freq_doc2(str(doc_id))
        for gram in grammar_config:
            run_tomita2(gram, str(doc_id))
            ner_feature.create_tomita_feature2(str(doc_id), grammar_config.keys())
        ner_feature.create_embedding_feature2(str(doc_id))
        ner_feature.create_morpho_feature2(str(doc_id))
exit()
# 3. Create answers for docs
session = Driver.db_session()
for set_doc in [training_set, dev_set]:
    for doc_id in db.get_set_docs(set_doc):
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        rb.morpho_doc(doc)
session.commit()
#
for set_doc in [training_set, dev_set]:
    for doc_id in db.get_set_docs(set_doc):
        rb.morpho_doc2(str(doc_id))
        rb.lemmas_freq_doc2(str(doc_id))
        for gram in grammar_config:
            run_tomita2(gram, str(doc_id))
        ner_feature.create_tomita_feature2(str(doc_id), grammar_config.keys())
        ner_feature.create_embedding_feature2(str(doc_id))
        ner_feature.create_morpho_feature2(str(doc_id))

for set_doc in [training_set, dev_set]:
    for doc_id in db.get_set_docs(set_doc):
        doc = session.query(Document).filter_by(doc_id=doc_id).first()
        print(doc_id)
        create_answers_feature_for_doc(doc, verbose=True)
session.commit()
exit()
#
# 4. NER Learning
#
NER.NER_person_learning()

# 5. NER + identification
# doc_id = u'414dc5e3-9508-4890-acf4-85277928097a'
# session = Driver.db_session()
# doc = session.query(Document).filter_by(doc_id=doc_id).first()
# # rb.morpho_doc(doc)
# # session.commit()
#
# settings = [[home_dir + '/weights/ner_oc1.params', home_dir + '/weights/ner_oc1.weights'],
#             [home_dir + '/weights/ner_oc2.params', home_dir + '/weights/ner_oc2.weights']]
#
# NER.NER_predict(doc, settings, session, verbose=True)
#
# print(doc.stripped)
# create_markup(doc, verbose=True)

# doc_id = u'eb9ab64f-6098-4bb2-9fef-17209dc689eb'
# session = Driver.db_session()
# doc = session.query(Document).filter_by(doc_id=doc_id).first()
# print(type(doc.markup))
# doc.markup.update({'1':1})

# print(doc.stripped)
# rb.morpho_doc(doc)
# session.commit()
# print(doc.morpho)
# create_answers_feature_for_doc(doc, session=session, verbose=True)
