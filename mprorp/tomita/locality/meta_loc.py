from mprorp.db.dbDriver import *
from mprorp.db.models import *
import re


def get_meta(doc):
    session = db_session()
    publisher = session.query(Publisher).filter(Publisher.pub_id == doc.publisher_id).first()
    try:
        address = publisher.meta['address']
        return {'region' : publisher.region, 'country' : publisher.country, 'name' : publisher.name, 'address' : address,
                'city' : re.findall('г\. ?(.*?),', address)}
    except:
        return {'region': publisher.region, 'country': publisher.country, 'name': publisher.name, 'address': 'No address'}

def see_all_meta():
    session = db_session()
    publishers = session.query(Publisher).all()
    print(len(publishers))
    line = 'Name    Region  Country Address\n'
    for publisher in publishers:
        try:
            line += publisher.name + '  ' + publisher.region + '    ' + publisher.country + '   ' + publisher.meta['address'] + '\n'
        except:
            print(publisher.meta, publisher.name)
    return line

#print(see_all_meta())