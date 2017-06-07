from mprorp.db.dbDriver import *
from mprorp.db.models import *


def locality_identification(fact):
    session = db_session()
    types = {'CityFact': 'Город'}
    kladr = session.query(Entity).filter(Entity.data['kladr_type'].astext == types[fact['type']]).all()
    print(len(kladr))
    codes = [str(i.entity_id).replace("UUID('", '').replace("')", '') for i in kladr if i.name.lower() == fact['norm']]
    if len(codes) != 0:
        return codes
    else:
        return ['Locality']