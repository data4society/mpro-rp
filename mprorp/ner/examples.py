from mprorp.ner.regular import regular_entities
from mprorp.tomita.regular import regular_tomita, grammar_count
import mprorp.analyzer.db as db

# regular processes with tomita
# doc_id = '000e82b8-6ea7-41f4-adc6-bc688fbbeeb6'
# for i in range(grammar_count):
#     regular_tomita(i, doc_id)

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
