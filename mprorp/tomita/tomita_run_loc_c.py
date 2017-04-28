import os
from mprorp.utils import home_dir, relative_file_path
import os.path as path
import subprocess as sp
from mprorp.tomita.tomita_run import create_file
from mprorp.config.settings import *
from mprorp.tomita.locality.tomita_out_loc import get_coordinates
from mprorp.tomita.locality.meta_loc import get_meta
from mprorp.tomita.locality.global_idetification import get_codes_from_kladr

def create_file_loc_c(doc, tomita_path):
    """function to create input file"""
    file_name = str(doc.doc_id) + '.txt'
    file = open(tomita_path + '/' + file_name, 'w', encoding='utf-8')
    text = doc.stripped
    file.write(text)
    file.close()
    return file_name

def create_config_loc(file_name, tomita_path):
    """function to create configuration file"""
    #path1 = os.path.dirname(os.path.realpath(__file__))
    #dic =  path1 + '/ovd/dic_ovd.gzt"'
    dic = relative_file_path(__file__, 'locality/dic_city.gzt')
    config_name = 'config_' + file_name[:-4] + '.proto'
    config_file = '''encoding "utf8";

TTextMinerConfig {
  Dictionary = "''' + dic + '''";
  Input = {
    File = "''' + file_name + '''";
  }
  Articles = [
  {Name = "Локация"}
  ]
  Facts = [
    { Name = "LocationFact_TOMITA" }
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

def start_tomita_loc_c(doc):
    """function to run tomita"""
    tomita_path = home_dir + '/tomita/tomita-parser-master/build/bin'
    work_path = os.getcwd()
    # создаем файл с текстом
    file_name = create_file(doc, tomita_path)
    # создаем config.proto
    create_config_loc(file_name, tomita_path)
    # запускаем tomitaparser.exe
    config = path.join(tomita_path, 'config_' + file_name[:-4] + '.proto')
    tomita = path.join(tomita_path, 'tomita-parser')
    os.chdir(tomita_path)
    if tomita_log_path:
        log_file = open(tomita_log_path, 'a')
        sp.call([tomita, config], stderr=sp.STDOUT, stdout=log_file)
        log_file.close()
    else:
        sp.call([tomita, config])
    os.chdir(work_path)
    output_name = 'facts_' + file_name[:-4] + '.xml'
    return output_name, file_name, tomita_path

def run_tomita_loc_c(doc):
    out_name, file_name, tomita_path = start_tomita_loc_c(doc)
    meta = get_meta(doc)
    results = get_coordinates(out_name, file_name, tomita_path)
    #for result in results:
    #    print(result)
    #    print(get_codes_from_kladr(result))
    return {'tomita' : results, 'meta' : meta}, tomita_path