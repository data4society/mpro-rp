"""start script for celery based running"""
from celery import Celery
import mprorp.config.celeryconfig as celeryconfig

from mprorp.db.dbDriver import *
from mprorp.db.models import *
import json
from mprorp.utils import relative_file_path


def load_app_conf(json_path, cur_config):
    with open(relative_file_path(__file__, json_path)) as app_config_file:
        config_list = json.load(app_config_file)
    config = {}
    session = db_session()
    session.execute("TRUNCATE TABLE sourcestatuses")
    session.commit()
    rubrics = session.query(Rubric).all()
    rubric_ids_by_names = {}
    for rubric in rubrics:
        rubric_ids_by_names[rubric.name] = str(rubric.rubric_id)
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
                    #source = crawler[source_type][source_key]
                    #source["ready"] = True
                    #source["next_crawling_time"] = 0
                    source_status = SourceStatus(app_id=app["app_id"], type=source_type, source_key=source_key)
                    session.add(source_status)
                    if "force_rubrication" in crawler[source_type][source_key]:
                        rubrics = crawler[source_type][source_key]["force_rubrication"]
                        rubric_ids = []
                        for rubr_name in rubrics:
                            rubric_ids.append(rubric_ids_by_names[rubr_name])
                        crawler[source_type][source_key]["force_rubrication"] = rubric_ids
        if "rubrication" in app:
            rubricator = app["rubrication"]
            new_rubricator = []
            for rubr_obj in rubricator:
                new_rubr_obj = {}
                new_rubr_obj["rubric_id"] = rubric_ids_by_names[rubr_obj["rubric"]]
                if "rubric_minus" in rubr_obj:
                    new_rubr_obj["rubric_minus_id"] = rubric_ids_by_names[rubr_obj["rubric_minus"]]
                new_rubr_obj["set_name"] = rubr_obj["set_name"]
                new_rubricator.append(new_rubr_obj)
            app["rubrication"] = new_rubricator

        if "rubrication_by_comparing" in app:
            app["rubrication_by_comparing"]["rubrics"]["good"] = rubric_ids_by_names[app["rubrication_by_comparing"]["rubrics"]["good"]]
            app["rubrication_by_comparing"]["rubrics"]["bad"] = rubric_ids_by_names[app["rubrication_by_comparing"]["rubrics"]["bad"]]

        config[app["app_id"]] = app
    variable_set(cur_config, config, session)
    session.commit()
    session.remove()


print("STARTING CELERY APP")
if sys.argv[0].split("/")[-1] != 'times.py':
    load_app_conf('config/app.json', 'last_config')

app = Celery('mprorp',
                 broker='amqp://',
                 # backend='amqp://',
                 )
app.config_from_object(celeryconfig)
# create Celery instance and load config
print("STARTING CELERY APP COMPLETE")

if __name__ == '__main__':
    pass;
    #app.start()
