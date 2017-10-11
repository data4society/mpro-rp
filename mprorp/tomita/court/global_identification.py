from mprorp.db.dbDriver import *
from mprorp.db.models import *
import math

def compare(arr1, arr2):
    for word in arr1:
        if word not in str(arr2):
            return False
    return True


def find_nearest_location(court, all_courts, locs):
    out = {}
    courts = [i for i in all_courts if court['norm'] in str(i.name.lower())]
    if len(courts) == 0:
        return {}
    elif len(courts) == 1:
        return {0: courts}
    else:
        for loc in locs:
            dist = min(math.fabs(court['fs'] - loc['ls']), math.fabs(loc['fs'] - court['ls']))
            for j in courts:
                if loc['norm'] in j.external_data['adr'].lower():
                    if dist in out:
                        out[dist].append(j)
                    else:
                        out[dist] = [j]
        return out


def court_identification(facts):
    out = {}
    session = db_session()
    all_courts = [i for i in session.query(Entity).filter(Entity.data["org_type"].astext == 'суд').all()
                 if i.external_data is not None]
    cities = [i for i in facts if i['type'] == 'CityFact']
    courts = [i for i in facts if i['type'] == 'CourtFact']
    print(cities)
    print(courts)
    for court in courts:
        court['norm'] = court['norm'].replace('«', '"')
        variants = find_nearest_location(court, all_courts, cities)
        print(variants)
        if variants != {}:
            best_dist = min([i for i in variants.keys()])
            if best_dist <= 250:
                out[str(court['fs'])+':'+str(court['ls'])] = \
                    str(variants[best_dist][0].entity_id).replace("UUID('", '').replace("')", '')
    return out
