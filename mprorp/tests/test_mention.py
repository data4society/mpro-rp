import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import mprorp.analyzer.rubricator as rb
import mprorp.analyzer.db as db

class SimpleDBTest(unittest.TestCase):

    def test_ention(self):

        dropall_and_create()

        # Создадим документ
        doc_stripped = 'Как писал Лев Толстой Федору Достоевскому. Алексей и Дмитрий Карамазовы напоминали ему друзей молодости Кузьмы Сергеевича Петрова-Водкина. Помощник Тэтчер Андрей Иванов.'
        my_doc = Document(stripped=doc_stripped, type='article')
        insert(my_doc)

        spans_word = {'Лев':         {'type': 'Имя',      'words': (0, 2, 2)},
                     'Толстой':      {'type': 'Фамилия',  'words': (0, 3, 3)},
                     'Федору':       {'type': 'Имя',      'words': (0, 4, 4)},
                     'Достоевскому': {'type': 'Фамилия',  'words': (0, 5, 5)},
                     'Алексей':      {'type': 'Имя',      'words': (1, 0, 0)},
                     'Дмитрий':      {'type': 'Имя',      'words': (1, 2, 2)},
                     'Карамазовы':   {'type': 'Фамилия',  'words': (1, 3, 3)},
                     'Кузьмы':       {'type': 'Имя',      'words': (1, 8, 8)},
                     'Сергеевича':   {'type': 'Отчество', 'words': (1, 9, 9)},
                     'Петрова':      {'type': 'Фамилия',  'words': (1, 10, 12)},
                     'Тэтчер':       {'type': 'Фамилия',  'words': (2, 1, 1)},
                     'Андрей':       {'type': 'Имя',      'words': (2, 2, 2)},
                     'Иванов':       {'type': 'Фамилия',  'words': (2, 3, 3)}}

        words_info = {(0, 2): [('им', 'ед')],
                     (0, 3):  [('им', 'ед')],
                     (0, 4):  [('дат', 'ед')],
                     (0, 5):  [('дат', 'ед')],
                     (1, 0):  [('им', 'ед')],
                     (1, 2):  [('им', 'ед')],
                     (1, 3):  [('им', 'мн')],
                     (1, 8):  [('род', 'ед'), ('им', 'мн')],
                     (1, 9):  [('вин', 'ед'), ('род', 'ед')],
                     (1, 10): [('вин', 'ед'), ('род', 'ед'), ('им', 'ед')],
                     (1, 12): [('вин', 'ед'), ('род', 'ед'), ('им', 'ед')],
                     (2, 1): [('им', 'ед')],
                     (2, 2): [('им', 'ед')],
                     (2, 3): [('им', 'ед')]}

        # Проведем морфологический анализ
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc(doc_id)
        morpho = db.get_morpho(doc_id)

        # Сформируем спаны
        spans = []
        for element in morpho:
            word = element.get('text', '')
            span_word = spans_word.get(word)
            if span_word != None:
                spans.append(span_word)

        mention = form_mention_of_span(spans, words_info)
        print(mention)
        turn_list_mention(mention)
        print(mention)
        remove_intersection_list_mention(mention)
        print(mention)

def form_mention_of_span(spans, words_info):

    # Формирует список упоминаний из спанов

    spans_info = form_spans_info(spans, words_info) # список информации для спанов

    mention = []

    for i in range(len(spans) - 1):

        first_span = spans[i]
        second_span = spans[i + 1]

        if (first_span['words'][0] == second_span['words'][0] and first_span['words'][2] + 1 == second_span['words'][1]):

            if (first_span['type'] == 'Имя' and second_span['type'] == 'Фамилия' or
                first_span['type'] == 'Имя' and second_span['type'] == 'Отчество' or
                first_span['type'] == 'Фамилия' and second_span['type'] == 'Имя'):

                first_span_info = spans_info[i]
                second_span_info = spans_info[i + 1]

                if exist_overall_info([first_span_info, second_span_info]):
                    mention.append([i, (i + 1)])

    for i in range(len(spans) - 2):

        first_span = spans[i]
        second_span = spans[i + 1]
        third_span = spans[i + 2]

        if (first_span['words'][0] == second_span['words'][0] and second_span['words'][0] == third_span['words'][0]
            and first_span['words'][2] + 1 == second_span['words'][1] and second_span['words'][2] + 1 == third_span['words'][1]):

            if (first_span['type'] == 'Имя' and second_span['type'] == 'Отчество' and third_span['type'] == 'Фамилия' or
                first_span['type'] == 'Фамилия' and second_span['type'] == 'Имя' and third_span['type'] == 'Отчество'):

                first_span_info = spans_info[i]
                second_span_info = spans_info[i + 1]
                third_span_info = spans_info[i + 2]

                if exist_overall_info([first_span_info, second_span_info, third_span_info]):
                    mention.append([i, (i + 1), (i + 2)])

    return mention

def form_spans_info(spans, words_info):

    # Формирует список информации для спанов по информации для слов

    spans_info = []

    for span in spans:

        all_span_info = [] # Общий список информации для всех слов спана

        sentence = span['words'][0]
        start_word = span['words'][1]
        end_word = span['words'][2]

        i = start_word
        while i <= end_word:
            word_info = words_info.get((sentence, i))
            if word_info != None:
                for element_word_info in word_info:
                    if element_word_info not in all_span_info:
                        all_span_info.append(element_word_info)
            i = i + 1

        span_info = []
        for element_all_span_info in all_span_info:
            flag = True
            i = start_word
            while i <= end_word:
                word_info = words_info.get((sentence, i))
                if word_info != None:
                    if element_all_span_info not in word_info:
                        flag = False
                        break
                i = i + 1
            if flag == True:
                span_info.append(element_all_span_info)

        spans_info.append(span_info)

    return spans_info

def exist_overall_info(spans_info):

    # Определяет есть ли общая инфа для спанов из spans_info

    all_span_info = []  # Общий список информации для всех спанов из spans_info
    for span_info in spans_info:
        for element_span_info in span_info:
            if element_span_info not in all_span_info:
                all_span_info.append(element_span_info)

    for element_all_span_info in all_span_info:
        Flag = True
        for span_info in spans_info:
            if element_all_span_info not in span_info:
                Flag = False
                break
        if Flag == True:
            return True

    return False

def turn_list_mention(mention):

    # Сворачивает список упоминаний
    del_list = []
    for i in range(len(mention)):
        for j in range(len(mention)):
            if i != j:
                if str(mention[i])[1:-1] in str(mention[j])[1:-1]:
                    if mention[i] not in del_list:
                        del_list.append(mention[i])

    for element_del_list in del_list:
        mention.remove(element_del_list)

def remove_intersection_list_mention(mention):

    del_list = []

    for i in range(len(mention) - 1):
        for j in mention[i]:
            if j in mention[i + 1]:
                if mention[i] not in del_list:
                    del_list.append(mention[i])
                if mention[i + 1] not in del_list:
                    del_list.append(mention[i + 1])

    for element_del_list in del_list:
        mention.remove(element_del_list)




