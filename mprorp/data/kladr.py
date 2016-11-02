"""script for import KLADR to database"""
import csv
import os
from mprorp.db.dbDriver import *
from mprorp.db.models import *

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
    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'/kladr_data/KLADR.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                parse_kladr_row(row, session)
            else:
                data = True

    with open(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'/kladr_data/STREET.csv', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                parse_kladr_row(row, session)
            else:
                data = True
    session.remove()

def parse_kladr_row(row, session):
    kladr_id = row[2]
    level = get_level(kladr_id)
    socr = row[1]
    socrs_level = socrs[str(level)]
    if socr in socrs_level:
        type = socrs[str(level)][socr]
    else:
        type = socr
    kladr = KLADR(kladr_id = kladr_id, name = row[0], type = type, level = level)
    session.add(kladr)
    session.commit()


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
        print(code)
        print("CCCCC")
        exit()
    for i in range(start_level, 0, -1):
        if get_part_from_code(code, i):
            return i
    print(code)
    print("BBBBB")
    exit()



if __name__ == '__main__':
    import_kladr()
