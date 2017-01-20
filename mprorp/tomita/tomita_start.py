"""function to create configuration files and run tomita"""
from os import chdir
from mprorp.utils import home_dir, relative_file_path
import os.path as path
import subprocess as sp
import re
import os
from mprorp.config.settings import *

# dictionary with directions to different tomita grammars
grammars = {'person.cxx': 'bin',
            'date.cxx': 'bin', #bin2
            'loc.cxx': 'bin', #bin3
            'adr.cxx': 'bin', #bin4
            'org.cxx': 'bin', #bin5
            'norm_act.cxx': 'bin', #bin6
            'prof.cxx': 'bin'} #bin7
# dictionary with dic_names of grammars
dic = {'person.cxx': '{Name = "FIO"}, {Name = "Персона"}',
       'date.cxx': '{Name = "DATE"}, {Name = "Дата"}',
       'loc.cxx': '{Name = "Локация"}',
       'adr.cxx': '{Name = "Адрес"}',
       'org.cxx': '{Name = "Организация"}',
       'norm_act.cxx': '{Name = "Нормативный Акт"}',
       'prof.cxx': '{Name = "Профессия"}'}
# dictionary with names of facts to extract
fact = {'person.cxx': '{ Name = "PersonFact_TOMITA" }',
        'date.cxx': '{ Name = "DateFact_TOMITA" }',
        'loc.cxx': '{ Name = "LocationFact_TOMITA" }',
        'adr.cxx': '{ Name = "AdrFact_TOMITA" }',
        'org.cxx': '{ Name = "OrgFact_TOMITA" }',
        'norm_act.cxx': '{Name = "NormFact_TOMITA"}',
        'prof.cxx': '{Name = "ProfFact_TOMITA"}'}


def create_config(grammar_name, file_name, tomita_path):
    """function to create configuration file"""
    #path1 = os.path.dirname(os.path.realpath(__file__))
    #path2 = path1 + '/grammars/dic_'
    path2 = relative_file_path(__file__, 'grammars/dic_')
    grammar = grammar_name + '.cxx'
    config_name = 'config_' + file_name[:-4] + '.proto'
    config_file = '''encoding "utf8";

TTextMinerConfig {
  Dictionary = "''' + path2 + grammar_name + '''.gzt"''' + ''';
  Input = {
    File = "''' + file_name + '''";
  }
  Articles = [
    ''' + dic[grammar] + '''
  ]
  Facts = [
    ''' + fact[grammar] + '''
  ]
  Output = {
    File =''' + ''' "facts_''' + file_name[:-4] + '''.txt";
    Format = text;
  }
}'''

    config = open(tomita_path + '/' + config_name, 'w', encoding='utf-8')
    config.write(config_file)
    config.close()


def create_file(doc, tomita_path):
    """function to create input file"""
    file_name = str(doc.doc_id) + '.txt'
    file = open(tomita_path + '/' + file_name, 'w', encoding='utf-8')
    text = doc.stripped
    file.write(text.replace('\n',''))
    file.close()
    return file_name


def start_tomita(grammar, doc):
    """function to run tomita"""
    tomita_path = home_dir + '/tomita/tomita-parser-master/build/bin'
    grammar_name = re.findall('(.*)\\.cxx', grammar)[0]
    work_path = os.getcwd()
    # создаем файл с текстом
    file_name = create_file(doc, tomita_path)
    # создаем config.proto
    create_config(grammar_name, file_name, tomita_path)
    # запускаем tomitaparser.exe
    config = path.join(tomita_path, 'config_' + file_name[:-4] + '.proto')
    tomita = path.join(tomita_path, 'tomita-parser')
    chdir(tomita_path)
    if tomita_log_path:
        log_file = open(tomita_log_path, 'w')
        sp.call([tomita, config], stderr=sp.STDOUT, stdout=log_file)
        log_file.close()
    else:
        sp.call([tomita, config])
    chdir(work_path)
    output_name = 'facts_' + file_name[:-4] + '.txt'
    return output_name, tomita_path