from mprorp.tomita.regular import grammar_count
import mprorp.analyzer.db as db
import mprorp.ner.feature as ner_feature
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


session = Driver.db_session()
res = session.query(Markup.markup_id).filter((Markup.type == '56')).distinct().all()

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