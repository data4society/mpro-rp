from mprorp.tomita.OVD.global_identification import step1
import os
from mprorp.utils import home_dir
import os.path as path
import subprocess as sp

def create_file_ovd(doc):
    """function to create input file"""
    file_name = str(doc.doc_id) + '.txt'
    file = open(file_name, 'w', encoding='utf-8')
    text = doc.stripped
    file.write(text)
    file.close()
    return file_name

def del_files_ovd(doc_id):
    """function to delete temporal files"""
    file_name1 = doc_id + '.txt'
    file_name2 = 'config_' + doc_id + '.proto'
    file_name3 = 'facts_' + doc_id + '.xml'
    os.remove(file_name1, dir_fd=None)
    os.remove(file_name2, dir_fd=None)
    os.remove(file_name3, dir_fd=None)

def create_config_ovd(file_name):
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

    config = open(config_name, 'w', encoding='utf-8')
    config.write(config_file)
    config.close()

def start_tomita_ovd(doc):
    """function to run tomita"""
    home_path = home_dir + '/tomita/tomita-parser-master/build'
    tomita_path = path.join(home_path, 'bin')
    os.chdir(tomita_path)
    # создаем файл с текстом
    file_name = create_file_ovd(doc)
    # создаем config.proto
    create_config_ovd(file_name)
    # запускаем tomitaparser.exe
    config = path.join(tomita_path, 'config_' + file_name[:-4] + '.proto')
    tomita = path.join(tomita_path, 'tomita-parser')
    sp.call([tomita, config])
    output_name = 'facts_' + file_name[:-4] + '.xml'
    return output_name, file_name

def run_tomita_ovd(doc, n=1):
    out_name, file_name = start_tomita_ovd(doc)
    results = step1(out_name, file_name, n)
    del_files_ovd(str(doc.doc_id))
    return results