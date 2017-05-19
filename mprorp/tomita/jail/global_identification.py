from mprorp.db.dbDriver import *
from mprorp.db.models import *


def jail_identification(fact):
    session = db_session()
    jails = session.query(Entity).filter(Entity.data["type"].astext == 'jail').all()
    for jail in jails:
        if fact['norm'] in jail.data['norm']:
            return str(jail.entity_id).replace("UUID('", '').replace("')", '')
    return 'jail'
