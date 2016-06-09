import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import mprorp.analyzer.rubricator as rb
import mprorp.analyzer.db as db
import subprocess as sp
import os.path as path
from os import getcwd
import os

p1 = getcwd()
p2 = 'aaa'
while (p2 != 'mprorp') and (p2 != ''):
    p1, p2 = path.split(p1)
if p2 == '':
    print('Not found')
else:
    gram_path = path.join(p1, p2, 'tomita_grammars', 'test_tomita', 'config.proto')
    # files = os.listdir(gram_path)
    # print(files)
    print(os.path.abspath(gram_path))
    tomita_path = '/home/tomita/tomita-parser-master/build/bin/'
    sp.call([tomita_path + 'tomita-parser', gram_path])
    # sp.call(tomita_path + 'tomita-parser')
    # os.listdir(gram_path)

class SimpleDBTest(unittest.TestCase):

    def test_tomita_load_files(self):
        dropall_and_create()
        files, config_file = tomita_files()
        db.put_tomita_grammar('тестовая грамматика', files, config_file)


def tomita_files():
    result = dict()
    result['config.proto'] = '''encoding "utf8"; // указываем кодировку, в которой написан конфигурационный файл
TTextMinerConfig {
  Dictionary = "mydic.gzt"; // путь к корневому словарю
  PrettyOutput = "PrettyOutput.html"; // путь к файлу с отладочным выводом в удобном для чтения виде
  Input = {
    File = "test.txt"; // путь к входному файлу
  }
  Articles = [
    { Name = "наша_первая_грамматика" } // название статьи в корневом словаре,
                                          // которая содержит запускаемую грамматику
  ]
}'''

    result['first.cxx'] = '''
#encoding "utf-8"    // сообщаем парсеру о том, в какой кодировке написана грамматика
#GRAMMAR_ROOT S      // указываем корневой нетерминал грамматики

S -> Adj Noun;'''

    result['mydic.gzt'] = '''encoding "utf8";               // указываем кодировку, в которой написан этот файл

import "base.proto";           // подключаем описания protobuf-типов (TAuxDicArticle и прочих)
import "articles_base.proto";  // Файлы base.proto и articles_base.proto встроены в компилятор.
                               // Их необходимо включать в начало любого gzt-словаря.

// статья с нашей грамматикой:
TAuxDicArticle "наша_первая_грамматика"
{
    key = { "tomita:first.cxx" type=CUSTOM }
}'''

    return result, 'config.proto'  # files list and config file name

