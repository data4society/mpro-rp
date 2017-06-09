from mprorp.db.dbDriver import *
from mprorp.db.models import *


def compare(arr1, arr2):
    for word in arr1:
        if word not in str(arr2):
            return False
    return True


def clean_fact(fact):
    fact = fact.replace(' №', '').replace('(', '').replace('"', '').replace(')', '')
    return fact


def jail_identification(fact):
    fact['norm'] = clean_fact(fact['norm'])
    session = db_session()
    jails = session.query(Entity).filter(Entity.data["org_type"].astext == 'jail').all()
    for jail in jails:
        if compare(fact['norm'].split(), jail.external_data['norm']):
            return str(jail.entity_id).replace("UUID('", '').replace("')", '')
    return 'org'
