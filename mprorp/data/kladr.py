"""script for import KLADR to database"""
import csv
import os
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from sqlalchemy.orm import load_only

from mprorp.analyzer.pymystem3_w import Mystem
from sqlalchemy.orm.attributes import flag_modified

socrs = dict()
def import_kladr():
    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '/kladr_data/SOCRBASE.csv',
              'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                level = row[0]
                if level not in socrs:
                    socrs[level] = dict()
                socrs[level][row[1]] = row[2]
            else:
                data = True

    session = db_session()
    n = 0
    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'/kladr_data/KLADR.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                n = parse_kladr_row(row, session, n)
            else:
                data = True

    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'/kladr_data/STREET.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                n = parse_kladr_row(row, session, n)
            else:
                data = True
    session.commit()
    session.remove()


def parse_kladr_row(row, session, n):
    kladr_id = row[2]
    level = get_level(kladr_id)
    socr = row[1]
    socrs_level = socrs[str(level)]
    if socr in socrs_level:
        type = socrs[str(level)][socr]
    else:
        type = socr
    kladr = KLADR(kladr_id = kladr_id, name = row[0], type = type, level = level)
    n+=1
    session.add(kladr)
    if n%10000 == 0:
        print(n)
        session.commit()
    return n


def import_ovds():
    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '/kladr_data/ovds_out.csv', 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + '/kladr_data/ovds.csv',
                  'r') as csvfile:
            spamreader = csv.reader(csvfile)
            session = db_session()
            n = 0
            for row in spamreader:
                #print(row[0])
                #exit()
                has_kladr = False
                for i in range(5, 1, -1):
                    if row[i]:
                        has_kladr = True
                        break
                if not(has_kladr and ((i==5 and len(row[i]) == 17) or (i!=5 and len(row[i]) == 13))):
                    print("KLADR ERROR", row)
                    continue
                data = dict()
                data["name"] = row[0]
                data["kladr"] = row[i]
                data["org_type"] = 'OVD'
                entity = Entity(name=row[0], data=data, entity_class='location')
                #continue
                session.add(entity)
                session.commit()
                row.append(entity.entity_id)
                spamwriter.writerow(row)
                n += 1
                print(n)


kladr_structure = {1: [0, 2], 2: [2, 5], 3: [5, 8], 4: [8, 11], 5: [11, 15]}
def get_part_from_code(code, level):
    range = kladr_structure[level]
    return int(code[range[0]:range[1]])


def get_level(code):
    if len(code) == 13:
        start_level = 4
    elif len(code) == 17:
        start_level = 5
    else:
        print(code, "ERROR")
        exit()
    for i in range(start_level, 0, -1):
        if get_part_from_code(code, i):
            return i
    print(code, "ERROR")
    exit()


def upd_kladr():
    mystem = Mystem()
    mystem.start()
    session = db_session()
    kladrs = session.query(KLADR).options(load_only("name")).limit(100).all()
    n = 0
    for kladr in kladrs:
        name = kladr.name
        lemmas = dict()
        morpho = mystem.analyze(name)
        #print(morpho)
        #exit()

        for i in morpho:
            # if this is a word
            if 'analysis' in i:
                for l in i.get('analysis', []):
                    if l.get('lex', False) and l.get('wt', 0) > 0:
                        lemmas[l['lex']] = lemmas.get(l['lex'], 0) + l.get('wt', 1)
        kladr.name_lemmas = lemmas
        n += 1
        if n % 10000 == 0:
            print(n)
            session.commit()



if __name__ == '__main__':
    #upd_kladr()
    #import_kladr()
    import_ovds()
