"""start script for NER learning"""
import sys
sys.path.insert(0, '..')
from mprorp.ner.NER import NER_person_learning, NER_learning_by_config
from mprorp.db.dbDriver import *


if __name__ == '__main__':
    print("STARTING NER LEARNING")
    #NER_person_learning()
    apps_config = variable_get("last_config")
    for app_id in apps_config:
        app = apps_config[app_id]
        if "ner_predict" in app:
            ner_settings = app["ner_predict"]["ner_settings"]
            for settings in ner_settings:
                print("START LEARNING WITH SETTINGS", settings)
                NER_learning_by_config(settings)
                print("COMPLETE LEARNING WITH SETTINGS", settings)
    print("LEARNING COMPLETE")
