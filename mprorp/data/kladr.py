"""script for import KLADR to database"""
import csv
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from sqlalchemy.orm import load_only

from mprorp.analyzer.pymystem3_w import Mystem

from mprorp.utils import relative_file_path

import pymorphy2
morph = pymorphy2.MorphAnalyzer()

mystem = Mystem()
mystem.start()
socrs = dict()
mvd_root = 'eaf0a69a-74d7-4e1a-9187-038a202c7698'
def import_kladr():
    print("start import kladrs")
    with open(relative_file_path(__file__, 'kladr_data/SOCRBASE.csv'), 'r') as csvfile:
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
    with open(relative_file_path(__file__, 'kladr_data/KLADR.csv'), 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                n = parse_kladr_row(row, session, n)
            else:
                data = True

    with open(relative_file_path(__file__, 'kladr_data/STREET.csv'), 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                n = parse_kladr_row(row, session, n)
            else:
                data = True
    session.commit()
    session.remove()
    print("fin import kladrs")


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
    print("start import ovds")
    with open(relative_file_path(__file__, 'kladr_data/ovds_out.csv'), 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open(relative_file_path(__file__, 'kladr_data/ovds.csv'),
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
                external_data = dict()
                data["name"] = row[0]
                external_data["kladr"] = row[i]
                data["jurisdiction"] = mvd_root
                entity = Entity(name=row[0], data=data, external_data=external_data, entity_class='org')
                #continue
                session.add(entity)
                session.commit()
                row.append(entity.entity_id)
                spamwriter.writerow(row)
                n += 1
                print(n)
    print("fin import ovds")


kladr_structure = {1: [0, 2], 2: [2, 5], 3: [5, 8], 4: [8, 11], 5: [11, 15]}
def get_part_from_code(code, level):
    range = kladr_structure[level]
    return code[range[0]:range[1]]


def get_level(code):
    if len(code) == 13:
        start_level = 4
    elif len(code) == 17:
        start_level = 5
    else:
        print(code, "ERROR")
        exit()
    for i in range(start_level, 0, -1):
        if int(get_part_from_code(code, i)):
            return i
    print(code, "ERROR")
    exit()


def get_parents_codes(code):
    level = get_level(code)
    codes = []
    cur_code = ""
    for i in range(1, level):
        part = get_part_from_code(code, i)
        cur_code += part
        if int(part):
            zeroes = '0' * (13-len(cur_code))
            full_cur_code = cur_code + zeroes
            codes.append(full_cur_code)
    return codes


def upd_kladr():
    print("start update kladrs")
    session = db_session()
    kladrs = session.query(KLADR).options(load_only("name")).all()
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
    print("fin update kladrs")


def upd_ovds_tables():
    print("start update ovds")
    with open(relative_file_path(__file__, 'kladr_data/ovds_out2.csv'), 'w') as csvnewfile:
        spamwriter = csv.writer(csvnewfile)
        with open(relative_file_path(__file__, '/kladr_data/ovds_out.csv'),
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
                kladr = row[i]
                codes = get_parents_codes(kladr)
                codes.append(kladr)
                full_address = []
                bad = False
                for code in codes:
                    #print(code)
                    try:
                        kladr_obj = session.query(KLADR).options(load_only("name","type")).filter_by(kladr_id=code).one()
                        full_address.append(geoobject_name(kladr_obj.name, kladr_obj.type))
                    except Exception as err:
                        print("Error with code", code, "from row", row)
                        full_address = "Error"
                        bad = True
                        break
                #print(full_address)
                #print(type(full_address))
                if type(full_address) is list:
                    if row[6]:
                        full_address.append(row[6])
                    full_address = ", ".join(full_address)
                #if bad:
                #    continue
                print(full_address)
                #print(row)
                #print(kladr)
                n += 1
                print(n)
                #continue
                #row.append(entity.entity_id)
                row.append(full_address)
                spamwriter.writerow(row)
    print("fin update ovds")


def get_kladr_examples():
    with open(relative_file_path(__file__, 'kladr_data/SOCRBASE.csv'),
              'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        data = False
        for row in spamreader:
            if data:
                level = row[0]
                if level not in socrs:
                    socrs[level] = dict()
                socrs[level][row[2]] = row[1]
            else:
                data = True

    session = db_session()
    #print(sorted(socrs.iteritems()))
    #for level in socrs:
    for level in sorted(socrs.keys()):
        print("LEVEL:", level)
        socrs_level = socrs[level]
        #for socr in socrs_level:
        for socr in sorted(socrs_level.keys()):
            #print("    TYPE:", socr)
            kladrs = session.query(KLADR).filter_by(type=socr).limit(10)
            for kladr in kladrs:
                #print("        " + kladr.name)
                #if kladr.name == "Табачные":
                print("        " + geoobject_name(kladr.name, kladr.type))
                #break


types_to_first = ["аал", "город", "поселение", "жилой район", "местечко", "микрорайон", "остров", "село", "садовое некоммерческое товарищество", "станица", "хутор", "гаражно-строительный кооператив", "дачное некоммерческое партнерство", "некоммерческое партнерство", "фермерское хозяйство", "ферма", "территория", "почтовое отделение", "городок", "железнодорожный пост", "железнодорожный разъезд", "жилая зона", "заимка", "населенный пункт", "погост", "животноводческая точка", "полустанок", "проселок", "строение", "участок"]
mystem_to_pymorphy = {"nomn":"им","sing":"ед","plur":"мн","masc":"муж","femn":"жен","neut":"сред"}
def geoobject_name(name, type):
    if type == "Чувашия" and name == "Чувашская Республика -":
        return "Чувашская Республика"
    type = type.lower()
    type = type.replace("муницип.образование","муниципальное образование")
    if type in name.lower():
        return name
    name_first = True
    for type0 in ["поселок", "платформа", "станция"]:
        #print(type, type0)
        if type0 in type:
            name_first = False
            #print("AAA", type)
            break
    if type in types_to_first:
        #print("AAA", type)
        name_first = False
    if name_first:
        name_morpho = mystem.analyze(name.lower())
        #print(name_morpho)
        name_is_a = False
        for token in reversed(name_morpho):
            if token["text"] in ["й", "я", "е"]:
                name_is_a = True
                a_number = "sing"
                if token["text"] == "й":
                    a_gender = "masc"
                elif token["text"] == "я":
                    a_gender = "femn"
                else:
                    a_gender = "neut"
                break
            if "analysis" in token:
                for p in morph.parse(token["text"]):
                    if p.tag.POS == "ADJF" and p.tag.case == "nomn" and p.score > 0.01:
                        #print(p)
                        name_is_a = True
                        a_number = p.tag.number
                        a_gender = p.tag.gender
                        break
                """
                for variant in token["analysis"]:
                    if "gr" in variant:
                        gr = variant["gr"]
                        #print(gr[0:2], gr)
                        if gr[0:2] == "A=":
                            name_is_a = True
                            break
                """
                break
        if name_is_a:
            type_morpho = mystem.analyze(type)
            #print(a_number, a_gender)
            #print(type_morpho)
            found = False
            for token in type_morpho:
                if "analysis" in token:
                    to_mystem = False
                    can_continue = False
                    #print(morph.parse(token["text"]))
                    for p in morph.parse(token["text"]):
                        if p.score > 0.01:
                            #print(p)
                            #print(p.tag.POS)
                            if p.tag.POS == "NOUN":
                                if p.tag.case == "nomn" and p.tag.number == a_number and (a_gender == None or p.tag.gender == a_gender):
                                    found = True
                            elif p.tag.POS == None:
                                to_mystem = True
                                break
                            elif p.tag.POS == "ADJF":
                                if p.tag.case == "nomn" and p.tag.number == a_number and (a_gender == None or p.tag.gender == a_gender):
                                    can_continue = True
                    if to_mystem:
                        for variant in token["analysis"]:
                            if "gr" in variant:
                                gr = variant["gr"]
                                # print(gr[0:2], gr)
                                if gr[0:1] == "S":
                                    if mystem_to_pymorphy["nomn"] in gr and mystem_to_pymorphy[a_number] in gr and (a_gender == None or mystem_to_pymorphy[a_gender]) in gr:
                                        found = True
                                elif gr[0:1] == "A":
                                    if mystem_to_pymorphy["nomn"] in gr and mystem_to_pymorphy[a_number] in gr and (a_gender == None or mystem_to_pymorphy[a_gender]) in gr:
                                        can_continue = True
                            else:
                                name_first = False
                    if not found:
                        if can_continue:
                            continue
                        name_first = False
                    break
        else:
            name_first = False
    if name_first:
        return name + " " + type
    else:
        return type + " " + name


if __name__ == '__main__':
    #print(mystem.analyze("ильгощинский"))
    #print(morph.parse("ильгощинский обрыв"))
    #import_kladr()
    #upd_kladr()
    #import_ovds()
    upd_ovds_tables()
    #get_kladr_examples()
    #session = db_session()
    #ovds = session.query(Entity).filter(Entity.data.has_key("org_type")).count()
    #print(ovds)
