from mprorp.db.dbDriver import *
from mprorp.db.models import *

from mprorp.analyzer.rubricator import regular_morpho, regular_lemmas, regular_rubrication

if "worker" in sys.argv:
    celery = True
else:
    celery = False


def router_func(doc_id, status):
    print("route:", doc_id, status)
    if status == 0:
        pass
    if status == 1:
        doc_id = str(doc_id)
        regular_morpho.delay(doc_id)
    if status == 2:
        regular_lemmas.delay(doc_id)
    if status == 3:
        regular_rubrication.delay(doc_id)
    if status == 4:
        doc = Document(doc_id = doc_id, status = 1000)
        update(doc)
