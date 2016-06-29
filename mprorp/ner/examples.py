from mprorp.ner.regular import regular_entities
from mprorp.tomita.regular import regular_tomita, grammar_count
import mprorp.analyzer.db as db
import mprorp.ner.feature as ner_feature
import mprorp.analyzer.rubricator as rb
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import mprorp.ner.morpho_to_vec as mystem_to_vec
from os.path import expanduser
import os
import mprorp.ner.tomita_to_markup as tomita_to_markup

# regular processes with tomita
# doc_id = '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'
# for i in range(grammar_count):
#     regular_tomita(i, doc_id)

# create tomita features
doc_id = '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'
rb.morpho_doc(doc_id)
print(db.get_morpho(doc_id))
ner_feature.create_tomita_feature(doc_id, ['date.cxx', 'person.cxx'])
tomita_to_markup.convert_tomita_result_to_markup(doc_id, ['person.cxx'])

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

home = expanduser("~")
print(os.getcwd())