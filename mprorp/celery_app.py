"""start script for celery based running"""
from celery import Celery
import mprorp.celeryconfig as celeryconfig

from mprorp.db.dbDriver import *
from mprorp.db.models import *
import json
from mprorp.utils import relative_file_path

with open(relative_file_path(__file__, 'config/app.json')) as app_config_file:
    config_list = json.load(app_config_file)
config = {}
session = db_session()
for app in config_list:
    """
    if "ner_predict" in app:
        ner_settings = app["ner_predict"]["ner_settings"]
        for ind1, val1 in enumerate(ner_settings):
            for ind2, val2 in enumerate(val1):
                ner_settings[ind1][ind2] = home_dir + '/weights/' + val2
    """
    if "crawler" in app:
        crawler = app["crawler"]
        for source_type in crawler:
            for source_key in crawler[source_type]:
                source = crawler[source_type][source_key]
                source["ready"] = True
                source["next_crawling_time"] = 0
    if "rubrication" in app:
        rubricator = app["rubrication"]
        new_rubricator = []
        for rubr_obj in rubricator:
            new_rubr_obj = {}
            rubric = session.query(Rubric).filter_by(name=rubr_obj["rubric"]).first()
            new_rubr_obj["rubric_id"] = rubric.rubric_id
            rubric = session.query(Rubric).filter_by(name=rubr_obj["rubric_minus"]).first()
            new_rubr_obj["rubric_minus_id"] = rubric.rubric_id
            new_rubr_obj["set_name"] = rubr_obj["set_name"]
            new_rubricator.append(new_rubr_obj)

        app["rubrication"] = new_rubricator
    config[app["app_id"]] = app
variable_set("last_config", config, session)
session.commit()
session.remove()

# create Celery instance and load config
print("STARTING CELERY APP")
app = Celery('mprorp',
             broker='amqp://',
             # backend='amqp://',
             )
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()
