from os import getcwd
from os import chdir
import os.path as path
import subprocess as sp
import re
from mprorp.analyzer.db import get_doc

grammars = {'person.cxx': 'bin',
            'date.cxx': 'bin2'}

dic = {'person.cxx': '{Name = "FIO"}, {Name = "Персона"}',
       'date.cxx': '{Name = "DATE"}, {Name = "Дата"}'}

fact = {'person.cxx': '{ Name = "PersonFact_TOMITA" }',
        'date.cxx': '{ Name = "DateFact_TOMITA" }'}

dic_grammar = {'person.cxx': '''TAuxDicArticle "Персона"
{
    key = { "tomita:person.cxx" type=CUSTOM }
}

TAuxDicArticle "FIO"
{
 key = {"alg:fio" type = CUSTOM}
}''',
               'date.cxx': '''TAuxDicArticle "Дата"
{
    key = { "tomita:date.cxx" type=CUSTOM }
}

TAuxDicArticle "DATE"
{
 key = {"alg:date" type = CUSTOM}
}'''}


def create_dic(grammar_name):
    dic_name = 'dic_' + grammar_name + '.gzt'
    dic_file = '''encoding "utf8";
import "base.proto";
import "articles_base.proto";
import "keywords.proto";
import "facttypes.proto";

''' + dic_grammar[grammar] + '''

month "Месяц"
{
 key = "Январь"|"Февраль"|"Март"|"Апрель"|"Май"|"Июнь"|"Июль"|"Август"|"Сентябрь"|"Октябрь"|"Ноябрь"|"Декабрь"
}

week "День недели"
{
 key = "Понедельник"|"Вторник"|"Среда"|"Четверг"|"Пятница"|"Суббота"|"Воскресенье"
}'''

    dictionary = open(dic_name, 'w', encoding='utf-8')
    dictionary.write(dic_file)
    dictionary.close()


def create_config(grammar_name, file_name):
    config_name = 'config_' + grammar_name + '.proto'
    config_file = '''encoding "utf8";

TTextMinerConfig {
  Dictionary = ''' + '''"dic_''' + grammar_name + '''.gzt"''' + ''';
  PrettyOutput = "debug.html";
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
    File =''' + ''' "facts_''' + grammar_name + '''.txt";
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
    tomita_path_now = getcwd()
    home_path = re.findall('^(.*)\\\\', tomita_path_now)[0]
    tomita_path = path.join(home_path, grammars[grammar])
    grammar_name = re.findall('(.*)\\.cxx', grammar)[0]
    chdir(tomita_path)
    # создаем файл с текстом
    file_name = create_file(doc_id)
    # создаем config.proto
    create_config(grammar_name, file_name)
    # создаем dic.gzt
    create_dic(grammar_name)
    # запускаем tomitaparser.exe
    config = path.join(tomita_path, 'config_' + grammar_name + '.proto')
    tomita = path.join(tomita_path, 'tomitaparser.exe')
    sp.call([tomita, config])
    output_name = 'facts_' + grammar_name + '.txt'
    return output_name





