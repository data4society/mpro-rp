from analyzer.pymystem3_w import Mystem
import db.dbDriver
from db.models import *

session = db.dbDriver.dbDriver.DBSession()

mi_doc_id = "7a721274-151a-4250-bb01-4a4772557d09"
text = session.query(Document).filter(Document.doc_id == mi_doc_id).one().doc_source

m = Mystem(disambiguation=False)
new_morpho = m.analyze(text)

some_doc = session.query(Document).filter(Document.doc_id == mi_doc_id).one()
some_doc.morpho = new_morpho
session.commit()

morpho = session.query(Document).filter(Document.doc_id == mi_doc_id).one().morpho

lemmas = {}
print(morpho)
for i in morpho:
    for l in i.get('analysis',[]):
        if l.get('lex',False):
            lemmas[l['lex']] = lemmas.get(l['lex'], 0) + l.get('wt', 1)

some_doc = session.query(Document).filter(Document.doc_id == mi_doc_id).one()
some_doc.lemmas = lemmas
session.commit()

lemmas_db = session.query(Document).filter(Document.doc_id == mi_doc_id).one().lemmas

print(lemmas_db)