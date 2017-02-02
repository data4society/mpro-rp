from mprorp.tomita.grammars.config import config as grammar_config
from mprorp.tomita.tomita_run import run_tomita2

from mprorp.db.models import *
from mprorp.db.dbDriver import *

session = db_session()
doc = session.query(Document).filter_by(doc_id='c8236b7e-b0a3-43c1-8601-cb57a055189d').first()
print(repr(doc.stripped))

for gram in grammar_config:
    print(gram)
    run_tomita2(gram, 'c8236b7e-b0a3-43c1-8601-cb57a055189d')
    print('done ' + str(gram))

