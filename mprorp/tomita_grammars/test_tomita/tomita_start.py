from os import chdir
from os.path import expanduser
import os.path as path
import subprocess as sp
import re
from mprorp.analyzer.db import get_doc

grammars = {'person.cxx': 'bin2',
            'date.cxx': 'bin'}

dic = {'person.cxx': '{Name = "FIO"}, {Name = "Персона"}',
       'date.cxx': '{Name = "DATE"}, {Name = "Дата"}'}

fact = {'person.cxx': '{ Name = "PersonFact_TOMITA" }',
        'date.cxx': '{ Name = "DateFact_TOMITA" }'}


def create_config(grammar_name, file_name):
    grammar = grammar_name + '.cxx'
    config_name = 'config_' + file_name[:-4] + '.proto'
    config_file = '''encoding "utf8";

TTextMinerConfig {
  Dictionary = ''' + '''"/vagrant/mprorp/tomita_grammars/test_tomita/dic_''' + grammar_name + '''.gzt"''' + ''';
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

    config = open(config_name, 'w', encoding='utf-8')
    config.write(config_file)
    config.close()

def create_file(doc_id):
    file_name = str(doc_id) + '.txt'
    file = open(file_name, 'w', encoding='utf-8')
    text = get_doc(doc_id)
    file.write(text)
    file.close()
    return file_name

def start_tomita(grammar, doc_id):
    home = expanduser("~")
    home_path = home + '/tomita/tomita-parser-master/build'
    tomita_path = path.join(home_path, grammars[grammar])
    grammar_name = re.findall('(.*)\\.cxx', grammar)[0]
    chdir(tomita_path)
    # создаем файл с текстом
    file_name = create_file(doc_id)
    # создаем config.proto
    create_config(grammar_name, file_name)
    # запускаем tomitaparser.exe
    config = path.join(tomita_path, 'config_' + file_name[:-4] + '.proto')
    tomita = path.join(tomita_path, 'tomita-parser')
    sp.call([tomita, config])
    output_name = 'facts_' + file_name[:-4] + '.txt'
    return output_name