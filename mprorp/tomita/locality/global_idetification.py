from mprorp.db.dbDriver import *
from mprorp.db.models import *


def locality_identification(fact):
    session = db_session()
    types = {'CityFact': 'Город'}
    kladr = session.query(KLADR).filter(KLADR.type == types[fact['type']]).all()
    print(len(kladr))
    codes = [i.kladr_id for i in kladr if i.name.lower() == fact['norm']]
    if len(codes) != 0:
        return codes
    else:
        return ['Locality']
