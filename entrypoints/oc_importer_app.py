"""start script for NER learning"""
import sys
sys.path.insert(0, '..')
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from os import listdir
from os.path import isfile, join
from mprorp.utils import home_dir


if __name__ == '__main__':
    print("STARTING OC IMPORT")
    session = db_session()
    mypath = home_dir+'/opencorpora'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    i = 0
    for name in onlyfiles:
        name_parts = name.split(".")
        if name_parts[-1] == 'txt':
            with open(mypath+'/'+name, 'r') as myfile:
                data = myfile.read()
            doc = Document(guid='OCNEW_'+name_parts[0], doc_source=data, stripped=data, status='1100', type='oc')
            markup = Markup(doc=doc, entity_classes=[], name=name_parts[0]+' from Opencorpora New', type='56')
            session.add(doc)
            session.add(markup)
            i += 1
            if i % 100 == 0:
                print(i)
                session.commit()
    print(i)
    session.commit()
    session.remove()
    print("IMPORT COMPLETE")
