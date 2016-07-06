from mprorp.ner.regular import regular_entities
from mprorp.tomita.regular import regular_tomita, grammar_count
import mprorp.analyzer.db as db
import mprorp.ner.feature as ner_feature
import mprorp.analyzer.rubricator as rb
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import mprorp.ner.morpho_to_vec as mystem_to_vec
import os
import mprorp.ner.tomita_to_markup as tomita_to_markup
from mprorp.tomita.tomita_run import run_tomita

# regular processes with tomita
# doc_id = '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'
# for i in range(grammar_count):
#     regular_tomita(i, doc_id)

# create tomita features
# doc_id = '75fa182d-7fbc-4ec7-bbfd-fc4d743e8834'
# rb.morpho_doc(doc_id)
# print(db.get_morpho(doc_id))
# print(db.get_doc(doc_id))
# grammars = ['date.cxx', 'person.cxx']
# run_tomita(grammars[0], doc_id)
# run_tomita(grammars[1], doc_id)
# ner_feature.create_tomita_feature(doc_id, ['date.cxx', 'person.cxx'])
# tomita_to_markup.convert_tomita_result_to_markup(doc_id, ['person.cxx'])

# Create embedding feature
# doc_id = '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'
# ner_feature.create_embedding_feature(doc_id)

# regular processes to create markup with references
# now: person with tomita, later: few classes with NER
# regular_entities(doc_id)

# getting embedding for word
# emb_id = 'first_test_embedding'
# lemma = 'туда_ADVPRO'
# print(db.get_word_embedding(emb_id, lemma))
# lemma = 'жизнь_S'
# print(db.get_word_embedding(emb_id, lemma))

# delete markups by id or type
# db.del_markup(markup_id='2c9f4e98-b861-4eb0-ab11-11c5e7ebbe6e')
# db.del_markup(markup_type='0')

# Create NER morpho features\
# mystem = Mystem(disambiguation=False)
# delta_wt = 0.01  # ignore gr if wt < delta_wt
#
# a = mystem.analyze('который')
# for word in a:
#     if 'analysis' in word.keys():
#         res = np.zeros(mystem_to_vec.vec_len)
#         for analyse in word['analysis']:
#             if analyse['wt'] < delta_wt:
#                 continue
#             print(analyse['wt'], analyse['gr'])
#             vectors = mystem_to_vec.analyze(analyse['gr'])
#             len_vectors = len(vectors)
#             for vec in vectors:
#                 delta = (analyse['wt'] / len_vectors)
#                 res += delta * vec
#         print(res)

# Create NER model
# embedding = 'first_test_embedding'  # id from table embeddings
# gazetteers = []  # ['gaz_1', 'gaz_2']
# tomita_facts = ['Person','Date']
# morpho_features = ['morpho']  #
# hyper_parameters = {'d_win': 2,  # Number of words before and past
#                     'd_wrd': 1000,  # Size of vector associate to word
#                     'n_1': 500, 'n_2': 10}
# model_id = db.put_ner_model(embedding, gazetteers, tomita_facts, morpho_features, hyper_parameters)

#
# import mprorp.db.dbDriver as Driver
# from mprorp.db.models import *
# session = Driver.DBSession()
# tr_set = []
# dev_set = []
# res = session.query(Document.doc_id).filter(Document.type == 'oc').all()
# count = 0
# for i in res:
#     if count < 10:
#         dev_set.append(str(i[0]))
#     else:
#         tr_set.append(str(i[0]))
#     count += 1
# print('train', db.put_training_set(tr_set))
# print('dev', db.put_training_set(dev_set))


from mprorp.tomita.grammars.config import config

tr_set = '7436d611-f196-403f-98a1-f17024e96d94' # docs with markup

# for doc_id in db.get_set_docs(tr_set):
#     print(doc_id)
#     rb.morpho_doc(doc_id)
#     rb.lemmas_freq_doc(doc_id)
#     for gram in config:
#         run_tomita(gram, str(doc_id))
#     ner_feature.create_tomita_feature(str(doc_id), config.keys())
#     ner_feature.create_embedding_feature(str(doc_id))

# doc_id = '0e01603e-0e1e-06c8-21a5-379ccc4dba69'
# # ner_feature.create_tomita_feature(doc_id, ['loc.cxx'])
# # tomita_to_markup.convert_tomita_result_to_markup(doc_id, ['loc.cxx'])
# markup = db.get_markup_from_doc(doc_id)
# for key in markup:
#     ref = markup[key]
#     print(type(ref['start_offset']), ref['start_offset'], ref['start_offset'] + ref['len_offset'])
#     break

doc_id = '1bff4e98-7f7f-473c-a405-0a4d35c06f35'

# print(doc_id)
# rb.morpho_doc(doc_id)
# rb.lemmas_freq_doc(doc_id)
# for gram in config:
#     run_tomita(gram, str(doc_id))
# ner_feature.create_tomita_feature(str(doc_id), config.keys())
# ner_feature.create_embedding_feature(str(doc_id))
# print(db.get_markup_from_doc(doc_id))

set_id = '7436d611-f196-403f-98a1-f17024e96d94'
set_id = u'199698a2-e3f4-48a8-aaaa-09778161c8c4'
# set_id = u'074c809b-208c-4fb4-851c-1e71d7f01b60'
# print(db.get_docs_text(doc_id))
# doc_id = '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'
for doc_id in db.get_set_docs(set_id):
    rb.morpho_doc(doc_id)
    ner_feature.create_embedding_feature(str(doc_id))
ner_feature.create_answers_feature(set_id)
