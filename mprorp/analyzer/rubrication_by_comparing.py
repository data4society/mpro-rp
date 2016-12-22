"""compare json and list fields"""
from mprorp.db.models import *


def reg_rubrication_by_comparing(doc, config, session):
    """compare all needed fields from doc an it's source"""
    rubrics = config["rubrics"]
    fields = config["fields_to_compare"]
    origin_doc = session.query(Document).filter_by(doc_id=doc.meta["source_record_id"]).one()
    good = "good"
    for field in fields:
        if not js_compare(getattr(origin_doc, field), getattr(doc, field)):
            good = "bad"
            break
    doc.rubric_ids = [rubrics[good]]


def ordered(obj):
   if isinstance(obj, dict):
       return sorted((k, ordered(v)) for k, v in obj.items())
   if isinstance(obj, list):
       return sorted(ordered(x) for x in obj)
   else:
       return obj


def js_compare(a, b):
   if ordered(a) == ordered(b):
       return True
   else:
       return False