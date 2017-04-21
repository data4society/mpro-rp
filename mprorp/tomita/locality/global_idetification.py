from mprorp.db.dbDriver import *
from mprorp.db.models import *


def get_codes_from_kladr(fact):
    session = db_session()
    kladr = session.query(KLADR).filter(KLADR.level == 5).all()
    print(set([i.type for i in kladr]))
    codes = [i.kladr_id for i in kladr if i.name.lower() == fact['norm']]
    return codes
