from mprorp.tomita.OVD.global_identification import step1
import os
from mprorp.utils import home_dir
import os.path as path
import subprocess as sp
from mprorp.tomita.tomita_run import create_file
from mprorp.analyzer.db import *

def create_file_ovd(doc, tomita_path):
    """function to create input file"""
    file_name = str(doc.doc_id) + '.txt'
    file = open(tomita_path + '/' + file_name, 'w', encoding='utf-8')
    text = doc.stripped
    file.write(text)
    file.close()
    return file_name

def del_files_ovd(doc_id, tomita_path):
    """function to delete temporal files"""
    file_name1 = doc_id + '.txt'
    file_name2 = 'config_' + doc_id + '.proto'
    file_name3 = 'facts_' + doc_id + '.xml'
    os.remove(tomita_path + '/' +file_name1, dir_fd=None)
    os.remove(tomita_path + '/' +file_name2, dir_fd=None)
    os.remove(tomita_path + '/' +file_name3, dir_fd=None)

def create_config_ovd(file_name, tomita_path):
    """function to create configuration file"""
    path1 = os.path.dirname(os.path.realpath(__file__))
    dic =  path1 + '/OVD/dic_ovd.gzt"'
    config_name = 'config_' + file_name[:-4] + '.proto'
    config_file = '''encoding "utf8";

TTextMinerConfig {
  Dictionary = "''' + dic + ''';
  Input = {
    File = "''' + file_name + '''";
  }
  Articles = [
  {Name = "ОВД"}
	,{Name = "Локация"}
  ]
  Facts = [
    { Name = "OVDFact_TOMITA" }, { Name = "LocationFact_TOMITA" }
  ]
  Output = {
    File =''' + ''' "facts_''' + file_name[:-4] + '''.xml";
    Format = xml;
    Encoding = "utf-8";
  }
}'''

    config = open(tomita_path + '/' + config_name, 'w', encoding='utf-8')
    config.write(config_file)
    config.close()

def start_tomita_ovd(doc):
    """function to run tomita"""
    tomita_path = home_dir + '/tomita/tomita-parser-master/build/bin'
    work_path = os.getcwd()
    # создаем файл с текстом
    file_name = create_file(doc, tomita_path)
    # создаем config.proto
    create_config_ovd(file_name, tomita_path)
    # запускаем tomitaparser.exe
    config = path.join(tomita_path, 'config_' + file_name[:-4] + '.proto')
    tomita = path.join(tomita_path, 'tomita-parser')
    os.chdir(tomita_path)
    tomita_script = [tomita, config]
    if 'tomita_log_path' and tomita_log_path:
        tomita_script.append('>& ' + tomita_log_path)
    sp.call(tomita_script)
    os.chdir(work_path)
    output_name = 'facts_' + file_name[:-4] + '.xml'
    return output_name, file_name, tomita_path

def run_tomita_ovd(doc, n=1):
    out_name, file_name, tomita_path = start_tomita_ovd(doc)
    results = step1(out_name, file_name, n, tomita_path)
    del_files_ovd(str(doc.doc_id), tomita_path)
    return results

def only_russia(doc, session):
    if session is None:
        session = db_session()
    publ_id = doc.publisher_id
    publ = session.query(Publisher).filter(Publisher.pub_id == publ_id).first()
    if publ is not None:
        if publ.country == 'Россия':
            return True
        else:
            return False
    else:
        return True