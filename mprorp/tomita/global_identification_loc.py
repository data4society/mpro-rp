from mprorp.db.dbDriver import *
from mprorp.db.models import *
import re

def codes_from_kladr(dic_facts, text):
    session = db_session()
    strings = {}
    out = {}
    for coord in dic_facts:
        strings[coord] = text[int(coord.split(':')[0]):int(coord.split(':')[1])]
    for fact in strings:

        codes = session.query(KLADR).filter(KLADR.name_lemmas.has_key(el), KLADR.type == 'Город').all()