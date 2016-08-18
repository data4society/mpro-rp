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
from mprorp.db.models import *
from mprorp.ner.identification import create_markup
from mprorp.utils import home_dir
from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup


doc_id = u'3f521888-1e9f-4afd-8427-9d353cb842de'
session = Driver.db_session()
doc = session.query(Document).filter_by(doc_id=doc_id).first()
print(doc.stripped)
grammars_of_tomita_classes = ['loc.cxx', 'org.cxx', 'norm_act.cxx']
create_markup(doc, session, False)
session.commit()
convert_tomita_result_to_markup(doc, grammars_of_tomita_classes, session=session, verbose=True)
print(doc.markup)
session.commit()
print(doc.markup)