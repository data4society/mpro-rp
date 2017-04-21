from mprorp.db.dbDriver import *
from mprorp.db.models import *
import re

def get_meta(doc):
    session = db_session()
    publisher = session.query(Publisher).filter(Publisher.pub_id == doc.publisher_id).first()
    return {'region' : publisher.region, 'country' : publisher.country, 'name' : publisher.name, 'address' : publisher.meta['address'],
            'city' : re.findall('г\. ?(.*?),', publisher.meta['address'])}
