from mprorp.db.dbDriver import *
from mprorp.db.models import *
import math


def compare(arr1, arr2):
    for word in arr1:
        if word not in str(arr2):
            return False
    return True


def clean_fact(fact):
    fact = fact.replace(' №', '-').replace('(', '').replace('"', '').replace(')', '')
    return fact


def jail_identification(fact):
    fact['norm'] = clean_fact(fact['norm'])
    session = db_session()
    jails = session.query(Entity).filter(Entity.data["org_type"].astext == 'jail').all()
    for jail in jails:
        if compare(fact['norm'].split(), jail.external_data['norm']):
            return str(jail.entity_id).replace("UUID('", '').replace("')", '')
    return 'org'


def find_nearest_location(jail, all_jails, locs):
    print(jail)
    out = {}
    jails = [i for i in all_jails if clean_fact(jail['norm']) in str(i.external_data['norm'])]
    if len(jails) == 0:
        return {}
    elif len(jails) == 1:
        return {0: jails}
    else:
        for loc in locs:
            dist = min(math.fabs(jail['fs'] - loc['ls']), math.fabs(loc['fs'] - jail['ls']))
            for j in jails:
                if loc['norm'] in j.data['location'].lower():
                    if dist in out:
                        out[dist].append(j)
                    else:
                        out[dist] = [j]
        return out


def jail_identification_new(facts):
    out = {}
    session = db_session()
    all_jails = session.query(Entity).filter(Entity.data["org_type"].astext == 'jail').all()
    cities = [i for i in facts if i['type'] == 'CityFact']
    print(cities)
    jails = [i for i in facts if i['type'] == 'JailFact']
    for jail in jails:
        jail['norm'] = jail['norm'].replace('«', '"')
        variants = find_nearest_location(jail, all_jails, cities)
        if variants != {}:
            best_dist = min([i for i in variants.keys()])
            if best_dist <= 250:
                out[str(jail['fs'])+':'+str(jail['ls'])] = str(variants[best_dist][0].entity_id).replace("UUID('", '').replace("')", '')
    return out
