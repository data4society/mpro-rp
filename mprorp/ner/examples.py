from mprorp.tomita.regular import grammar_count
import mprorp.analyzer.db as db
import mprorp.ner.NER as NER
import mprorp.analyzer.rubricator as rb
from mprorp.analyzer.pymystem3_w import Mystem
import numpy as np
import mprorp.ner.morpho_to_vec as mystem_to_vec
import os
import mprorp.ner.tomita_to_markup as tomita_to_markup
from mprorp.tomita.tomita_run import run_tomita2
from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.ner.identification import create_answers_feature_for_doc_2

import mprorp.db.dbDriver as Driver
from mprorp.db.models import *
from mprorp.analyzer.db import put_training_set
from gensim.models import word2vec


session = Driver.db_session()
res = session.query(Markup.markup_id).filter((Markup.type == '56')).distinct().all()

config = NER.Config()
model_w2v = word2vec.Word2Vec.load_word2vec_format(config.pre_embedding_from_file, binary=True)
count = 0
print('Всего', len(model_w2v.vocab), 'слов')
session.add(Embedding(emb_id = 'second_embedding_1000', name = 'Вторая модель, загруженная с http://ling.go.mail.ru/'))
for word in model_w2v.vocab:
    session.add(WordEmbedding(lemma=word, embedding='second_embedding_1000', vector=[float(i) for i in model_w2v[word]]))
    count += 1
    if count % 1000 == 0:
        session.commit()
        print(count)
session.commit()
print(count)
res = session.query(WordEmbedding.lemma).filter(WordEmbedding.embedding == 'second_embedding_1000').all()
print(len(res))
exit()
    # wv_dict[word] = model_w2v[word]

print(db.is_name('василий'))
print(db.is_name('Иван'))
print(db.is_name('иван'))
exit()
classes = set()
count = 0
for r in res:
    count +=1
    if count > 5:
        break
    refs = db.get_references_for_doc(r.markup_id, session=session)
    for ref in refs:
        classes.add(ref[2])
        print(ref)
print(classes)