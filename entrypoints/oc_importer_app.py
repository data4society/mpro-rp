"""start script for NER learning"""
import sys
sys.path.insert(0, '..')
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from os import listdir
from os.path import isfile, join
from mprorp.utils import home_dir


def import_docs_and_markups():
    session = db_session()
    mypath = home_dir + '/opencorpora'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    i = 0
    for name in onlyfiles:
        name_parts = name.split(".")
        if name_parts[-1] == 'txt':
            with open(mypath + '/' + name, 'r') as myfile:
                data = myfile.read()
            doc = Document(guid='OCNEW_' + name_parts[0], doc_source=data, stripped=data, status='1100', type='oc')
            markup = Markup(doc=doc, entity_classes=[], name=name_parts[0] + ' from Opencorpora New', type='56')
            session.add(doc)
            session.add(markup)
            i += 1
            if i % 100 == 0:
                print(i)
                session.commit()
    print(i)
    session.commit()
    session.remove()


def import_references():
    session = db_session()
    markups = select([Markup.document, Markup.name], Markup.type == '56').fetchall()
    print(len(markups))
    mypath = home_dir + '/opencorpora'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    i = 0
    for markup in markups:
        i += 1
        name = markup[1].split(" ")[0]+".spans"
        if name in onlyfiles:
            with open(mypath + '/' + name, 'r') as myfile:
                data = myfile.read()
            lines = data.split("\n")
            lines = [line.strip('\t\n\r').strip() for line in lines]
            lines = [line for line in lines if line]
            for line in lines:
                segments = line.split(" ")
                reference = Reference()
                reference.outer_id = segments[0]
                reference.entity_class = int(segments[1])
                reference.start_offset = int(segments[2])
                reference.length_offset = int(segments[3])
                reference.end_offset = reference.start_offset + reference.length_offset
                reference.markup = markup[0]
                session.add(reference)
        else:
            print(name)
        if i % 100 == 0:
            print(i)
            session.commit()
    print(i)
    session.commit()
    session.remove()


if __name__ == '__main__':
    print("STARTING OC IMPORT")
    #import_docs_and_markups()
    import_references()
    print("IMPORT COMPLETE")
