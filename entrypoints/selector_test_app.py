"""test selector sources"""
import sys
sys.path.insert(0, '..')
from mprorp.crawler.selector import selector_start_parsing
from mprorp.db.dbDriver import *


if __name__ == '__main__':
    print("STARTING SELECTOR TEST")
    #NER_person_learning()
    session = db_session()
    apps_config = variable_get("last_config")
    test_arrs = []
    for app_id in apps_config:
        app = apps_config[app_id]
        if "crawler" in app:
            crawler = app["crawler"]
            if "selector" in crawler:
                selector = crawler["selector"]
                for source_key in selector:
                    for pattern in selector[source_key]["patterns"]:
                        test_arrs.append([source_key, pattern])

    for test_arr in test_arrs:
        print(test_arr)
        links = selector_start_parsing(test_arr[0], [test_arr[1]], 'test', session, True)
        for link in links:
            print(link)
        if len(links) == 0:
            print('________!!!NO LINKS!!!________')
    session.remove()

    print("SELECTOR TEST COMPLETE")
