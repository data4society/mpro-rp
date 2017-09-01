"""csv parser"""
from mprorp.db.models import *
from mprorp.db.dbDriver import *
import urllib.parse as urlparse

import csv
from mprorp.utils import relative_file_path
from mprorp.crawler.utils import check_url_with_blacklist
import datetime


def from_csv_start_parsing(source_name, app_id, session):
    """parse csv and add url by portions"""

    docs = []
    guids = []
    item_nums = variable_get("item_nums_csv_"+source_name)
    if session.query(Document).filter(Document.app_id == app_id, Document.status != 0).count() == item_nums:
        with open('/home/mprorp/data/csv/'+source_name, 'r', encoding='utf-8') as csvfile:
            spamreader = csv.reader(csvfile, delimiter='\t')
            i = 0
            for row in spamreader:
                if i < item_nums:
                    i += 1
                    continue
                if i == item_nums+10000:
                    break
                i += 1
                url = row[0]
                guid = app_id + url
                if url.find('http') != 0:
                    url = 'http://'+url
                #date = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())
                if guid not in guids:
                    guids.append(guid)
                    if session.query(Document).filter_by(guid=guid).count() == 0:
                        meta = dict()
                        parsed_uri = urlparse.urlparse(url)
                        publisher_name = parsed_uri.netloc
                        meta["publisher"] = {"name": publisher_name}
                        doc = Document(guid=guid, app_id=app_id, url=url, title=row[1], status=0, type='article', meta=meta)

                        publisher = session.query(Publisher).filter_by(name=publisher_name).first()
                        if publisher:
                            doc.publisher_id = str(publisher.pub_id)
                        else:
                            publisher = Publisher(name=publisher_name, site=publisher_name, country=publisher_name[publisher_name.rfind('.')+1:])
                            doc.publisher = publisher
                            session.add(publisher)

                        session.add(doc)
                        docs.append(doc)
        variable_set("item_nums_csv_" + source_name, i)
    return docs


if __name__ == '__main__':
    session = db_session()
    from_csv_start_parsing('mpro-urls_to_csv', 'test', session)
    session.commit()
    session.remove()