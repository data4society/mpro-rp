"""csv parser"""
from mprorp.db.models import *
from mprorp.db.dbDriver import *
import urllib.parse as urlparse

import csv
from mprorp.utils import relative_file_path
from mprorp.crawler.utils import check_url_with_blacklist, normalize_url
import datetime


def from_csv_start_parsing(source_name, app_id, session):
    """parse csv and add url by portions"""

    docs = []
    guids = []
    guids_urls = []
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
                title = row[0]
                if url.find('http') != 0:
                    url = 'http://'+url
                url = normalize_url(url)
                guid = app_id + url

                if guid not in guids:
                    guids.append(guid)
                    guids_urls.append((guid, url, title))
        if guids:
            result = session.query(Document.guid).filter(Document.guid.in_(guids)).all()
            result = [res[0] for res in result]
            guids_urls = [elem for elem in guids_urls if elem[0] not in result]
            if guids_urls:

                publishers = [urlparse.urlparse(elem[1]).netloc + "a" for elem in guids_urls]
                publisher_names = list(set(publishers))
                result = session.query(Publisher.name, Publisher.pub_id).filter(
                    Publisher.name.in_(publisher_names)).all()
                old_publishers = {res[0]: str(res[1]) for res in result}
                new_publishers = [publisher_name for publisher_name in publisher_names if
                                  publisher_name not in old_publishers]

                k = 0
                for elem in guids_urls:
                    guid = elem[0]
                    url = elem[1]
                    title = elem[2]
                    meta = dict()
                    publisher_name = publishers[k]
                    meta["publisher"] = {"name": publisher_name}
                    doc = Document(guid=guid, app_id=app_id, url=url, title=title, status=0, type='article', meta=meta)

                    if publisher_name in new_publishers:
                        publisher = Publisher(name=publisher_name, site=publisher_name,
                                              country=publisher_name[publisher_name.rfind('.') + 1:])
                        doc.publisher = publisher
                        session.add(publisher)
                    else:
                        doc.publisher_id = old_publishers[publisher_name]

                    session.add(doc)
                    docs.append(doc)
                    k += 1
        variable_set("item_nums_csv_" + source_name, i)
    return docs


if __name__ == '__main__':
    session = db_session()
    from_csv_start_parsing('mpro-urls_to_csv', 'test', session)
    session.commit()
    session.remove()