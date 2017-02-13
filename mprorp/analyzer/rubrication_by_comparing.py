"""compare json and list fields"""
from mprorp.db.models import *


def reg_rubrication_by_comparing(doc, config, session):
    """compare all needed fields from doc an it's source"""
    rubrics = config["rubrics"]
    fields = config["fields_to_compare"]
    origin_doc = session.query(Document).filter_by(doc_id=doc.meta["source_record_id"]).one()
    good = "good"
    for field in fields:
        if not js_compare(uu_to_str(getattr(origin_doc, field)), uu_to_str(getattr(doc, field))):
            good = "bad"
            break
    if doc.rubric_ids:
        rubric_ids = list(doc.rubric_ids)
    else:
        rubric_ids = list()
    rubric_ids.append(rubrics[good])
    doc.rubric_ids = rubric_ids

def uu_to_str(arr):
    return [str(i) for i in arr]

def ordered(obj):
   if isinstance(obj, dict):
       return sorted((k, ordered(v)) for k, v in obj.items())
   if isinstance(obj, list):
       return sorted(ordered(x) for x in obj)
   else:
       #print(repr(obj))
       return obj


def js_compare(a, b):
   if ordered(a) == ordered(b):
       return True
   else:
       return False


if __name__ == '__main__':
    from mprorp.db.dbDriver import *
    """
    session = db_session()
    import json  # or `import simplejson as json` if on Python < 2.6

    json_string = u'{"rubrics": {"good": "интернет","bad": "No name"},"fields_to_compare":["stripped"]}'
    obj = json.loads(json_string)
    reg_rubrication_by_comparing(doc, obj, session)
    """
    session = db_session()
    doc = session.query(Document).filter_by(doc_id='17d3217d-e2a6-4fe7-a2cc-7a8abb959cee').first()
    #doc_id = str(session.query(Record).filter_by(document_id='f5cab453-dd0b-0f51-8320-68314b4aa773').first().source)
    #doc = session.query(Document).filter_by(doc_id=doc_id).first()
    #print(repr(doc.stripped))
    #doc.stripped = doc.stripped.replace(u' ', u'\xa0')
    #session.commit()
    print(repr(doc.stripped))