import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
import mprorp.ner.feature as ner_feature


class SimpleDBTest(unittest.TestCase):

    def test_gazetteer_feature(self):
        dropall_and_create()
        doc_id, gaz_id = fill_db()
        rb.morpho_doc(doc_id)
        morpho = db.get_morpho(doc_id)
        print(morpho)
        ner_feature.create_gazetteer_feature(doc_id, gaz_id)
        ner_feature.create_gazetteer_feature(doc_id, gaz_id)


def fill_db():
    gaz_id = db.put_gazetteer('Числительные',
                     ['первый', 'второй', 'третий', 'четвертый', 'пятый', 'шестой', 'седьмой', 'восьмой', 'девятый',
                      'десятый','одиннадцатый', 'двенадцатый', 'тринадцатый', 'четырнадцатый', 'пятнадцатый',
                      'шестнадцатый', 'семнадцатый', 'восемнадцатый', 'девятнадцатый', 'двадцатый', 'тридцатый',
                      'сороковой', 'пятидесятый', 'шестидесятый', 'семидесятый', 'восьмидесятый', 'девяностый',
                      'сотый', 'сотенный', 'двухсотый', 'трехсотый', 'четырехсотый', 'пятисотый', 'шестисотый',
                      'семисотый', 'восьмисотый', 'девятисотый', 'тысячный', 'двухтысячный', 'трехтысячный',
                      'четырехтысячный', 'пятитысячный', 'шеститысячный', 'семитысячный', 'восьмитысячный',
                      'девятитысячный', 'десятитычячный', 'одиннадцатитысячный', 'двенадцатитысячный',
                      'тринадцатитысячный', 'четырнадцатитысячный', 'пятнадцатитысячный', 'шестнадцатитысячный',
                      'семнадцатитысячный', 'восемнадцатитысячный', 'девятнадцатитысячный', 'двадцатитысячный',
                      'тридцатитысячный', 'сорокатысячный', 'пятидесятитысячный', 'шестидесятитысячный',
                      'семидесятитысячный', 'восьмидесятитысячный', 'двевяностотысячный', 'стотысячный',
                      'двухсоттысячный', 'трехсоттысячный', 'четырехсоттысячный', 'потисоттысячный', 'полумиллионный',
                      'шестисоттысячный', 'семисоттысячный', 'восьмисоттысячный', 'девятисоттысячный', 'миллионный',
                      'первое', 'второе',
                      'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять',
                      'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать', 'пятнадцать', 'шестнадцать',
                      'семнадцать', 'восемнадцать', 'девятнадцать', 'двадцать', 'тридцать', 'сорок', 'пятьдесят',
                      'полста',
                      'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто', 'сто', 'двести', 'триста',
                      'четыреста', 'пятьсот', 'шестьсот', 'семьсот', 'восемьсот', 'девятьсот', 'тысяча',
                      'миллион', 'миллиард', 'десятка', 'сотня', 'дюжина', 'единица', 'двойка', 'тройка', 'четверка',
                      'пятерка', 'шестерка', 'семерка', 'восьмерка', 'девятка'])

    doc_db = Document(
        stripped='Первая девушка написала второму парню 3-е письмо одиннадцатого!!!  Ответ она ждала две недели.',
        type='article')
    insert(doc_db)
    return doc_db.doc_id, gaz_id
