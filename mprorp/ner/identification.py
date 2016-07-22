import mprorp.analyzer.db as db
import mprorp.ner.feature as feature
import mprorp.ner.morpho_to_vec as morpho_to_vec
import numpy as np

def identification_for_doc_id (doc_id):

    feature_type = feature.ner_feature_types['OpenCorpora']

    features = ['oc_feature_last_name', 'oc_feature_first_name', 'oc_feature_middle_name', 'oc_feature_nickname',
                'oc_feature_foreign_name', 'oc_feature_post', 'oc_feature_role', 'oc_feature_status']

    # Получим свойства слов документа из БД
    doc_properties = db.get_ner_feature_for_features(doc_id, feature_type, features)
    print('Свойства слов документа:', doc_properties)

    # Сформируем информацию о словах документа (падеж, число, нормальная форма)
    doc_properties_info = form_doc_properties_info(doc_id, doc_properties)
    print('Информация о словах документа:', doc_properties_info)

    # Сформиреум спаны
    spans = form_spans(doc_properties)
    print('Спаны:', spans)

    # Сформируем информацию о спанах (падеж, число, нормальная форма)
    spans_info = form_spans_info(spans, doc_properties_info)
    print('Информация о спанах:', spans_info)

    # Сформируем оценки связей спанов
    evaluations = form_evaluations(spans, spans_info)
    print('Оценки связей:', evaluations)

    # Сформируем список цепочек спанов
    list_chain_spans = form_list_chain_spans(spans, evaluations)
    print('Цепочки спанов:', list_chain_spans)

def form_doc_properties_info(doc_id, doc_properties):
    # Формирует информацию о словах документа

    doc_morpho = db.get_morpho(doc_id)

    doc_properties_info = {}

    for doc_property in doc_properties:

        for element_doc_morpho in doc_morpho:

            sentence_index = element_doc_morpho.get('sentence_index', -1)
            word_index = element_doc_morpho.get('word_index', -1)

            if sentence_index == -1 or word_index == -1:
                continue

            if doc_property[0] == sentence_index and doc_property[1] == word_index:

                analysis = element_doc_morpho.get('analysis')
                if not analysis is None:

                    list_lex = []
                    array_case = np.zeros((9))
                    array_numeric = np.zeros((2))

                    for analyse in analysis:

                        # Наполняем список лемм
                        current_lex = analyse.get('lex', '')
                        if current_lex != '':
                            if current_lex not in list_lex:
                                list_lex.append(current_lex)

                        vectors = morpho_to_vec.analyze(analyse['gr'])
                        len_vectors = len(vectors)

                        # Формируем массивы пажедей и чисел
                        for vector in vectors:
                            array_case = array_case + vector[3:12]
                            array_numeric = array_numeric + vector[12:14]

                    array_case /= len_vectors
                    array_numeric /= len_vectors

                    doc_properties_info[doc_property] = {'list_lex': list_lex, 'case': array_case, 'numeric': array_numeric}

    return doc_properties_info

def form_spans(doc_properties):
    # Формирует спаны

    spans_list = []
    for i in range(len(doc_properties)):
        doc_property = doc_properties[i]
        find = False
        for span in spans_list:
            if (span[0] == doc_property[0]) and (span[2] + 1 == doc_property[1]) and span[3] == doc_property[2]:
                span[2] += 1
                find = True
        if not find:
            spans_list.append([doc_property[0], doc_property[1], doc_property[1], doc_property[2]])

    spans = []
    for element_spans_list in spans_list:
        spans.append(tuple(element_spans_list))

    return spans

def form_spans_info(spans, doc_properties_info):
    # Формирует информацию о спанах

    spans_info = {}

    for span in spans:

        span_sentence_index = span[0]
        span_word_start_index = span[1]
        span_word_end_index = span[2]
        span_feature = span[3]

        list_lex = []
        array_case = np.zeros((9))
        array_numeric = np.zeros((2))

        word_index = span_word_start_index - 1
        while word_index <= span_word_end_index:

            word_index += 1

            doc_property = doc_properties_info.get((span_sentence_index, word_index, span_feature))
            if not doc_property is None:
                list_lex.extend(doc_property.get('list_lex'))
                array_case += doc_property.get('case')
                array_numeric += doc_property.get('numeric')

        array_case /= (span_word_end_index - span_word_start_index + 1)
        array_numeric /= (span_word_end_index - span_word_start_index + 1)

        spans_info[span] = {'list_lex': list_lex, 'case': array_case, 'numeric': array_numeric}

    return spans_info

def form_evaluations(spans, spans_info):
    # Формирует оценки связей спанов

    spans_len = len(spans)

    evaluations = []

    i = -1
    while i < spans_len - 2:

        i += 1
        first_span = spans[i]

        first_span_sentence_index = first_span[0]
        first_span_word_index_start = first_span[1]
        first_span_word_index_end = first_span[2]
        first_span_feature = first_span[3]

        j = i
        while j < spans_len - 1:

            j += 1
            second_span = spans[j]

            second_span_sentence_index = second_span[0]
            second_span_word_index_start = second_span[1]
            second_span_word_index_end = second_span[2]
            second_span_feature = second_span[3]

            # Различающимся фамилиям, именам, отчествам ставим -1
            if (first_span_feature == second_span_feature and first_span_feature in ['oc_feature_last_name',
                                                                                     'oc_feature_first_name',
                                                                                     'oc_feature_middle_name']):
                if not same_meanings_spans(first_span, second_span, spans_info):
                    evaluations.append([i, j, -1])
                    continue

            if first_span_sentence_index == second_span_sentence_index: # Спаны находятся в одном предложении

                # вложенные спаны
                if ((second_span_word_index_start <= first_span_word_index_start <= second_span_word_index_end and
                     second_span_word_index_start <= first_span_word_index_end <= second_span_word_index_end)
                    or
                    (first_span_word_index_start <= second_span_word_index_start <= first_span_word_index_end and
                     first_span_word_index_start <= second_span_word_index_end <= first_span_word_index_end)):

                    evaluations.append([i, j, -1])
                    continue

                # Стоящие рядом слова
                if first_span_word_index_end + 1 == second_span_word_index_start:

                    if first_span_feature == 'oc_feature_last_name' and second_span_feature == 'oc_feature_first_name': # Фамилия, Имя

                        if same_case_numeric(first_span, second_span, spans_info): # Одинаковый падеж, число
                            evaluations.append([i, j, 5])
                            continue
                        elif subjective_case(first_span, spans_info) or subjective_case(second_span, spans_info): # Фамилия или Имя в им.падеже
                            evaluations.append([i, j, 3])
                            continue

                    if first_span_feature == 'oc_feature_first_name' and second_span_feature == 'oc_feature_last_name':  # Имя, Фамилия

                        if same_case_numeric(first_span, second_span, spans_info):  # Одинаковый падеж, число
                            evaluations.append([i, j, 5])
                            continue
                        elif subjective_case(first_span, spans_info) or subjective_case(second_span, spans_info): # Фамилия или Имя в им.падеже
                            evaluations.append([i, j, 3])
                            continue

                    if first_span_feature == 'oc_feature_first_name' and second_span_feature == 'oc_feature_middle_name':  # Имя, Отчество

                        if same_case_numeric(first_span, second_span, spans_info):  # Одинаковый падеж, число
                            evaluations.append([i, j, 5])
                            continue
                        elif subjective_case(first_span, spans_info):  # Имя в им.падеже
                            evaluations.append([i, j, 3])
                            continue

                    # Роль, статус, должность перед именем, фамилией, иностр.именем, ником
                    if (first_span_feature in ['oc_feature_role', 'oc_feature_post', 'oc_feature_status'] and
                                second_span_feature in ['oc_feature_first_name', 'oc_feature_last_name',
                                                        'oc_feature_foreign_name', 'oc_feature_nickname']):
                        evaluations.append([i, j, 4])
                        continue

                # Стоящие рядом спаны
                if j == i + 1:

                    # Роль, статус, должность в одном предложении с именем, отчеством, фамилией, иностр.именем, ником
                    if (first_span_feature in ['oc_feature_role', 'oc_feature_post', 'oc_feature_status'] and
                                second_span_feature in ['oc_feature_first_name', 'oc_feature_last_name',
                                                        'oc_feature_middle_name',
                                                        'oc_feature_foreign_name', 'oc_feature_nickname'] or
                                    first_span_feature in ['oc_feature_first_name', 'oc_feature_last_name',
                                                           'oc_feature_middle_name',
                                                           'oc_feature_foreign_name', 'oc_feature_nickname'] and
                                    second_span_feature in ['oc_feature_role', 'oc_feature_post', 'oc_feature_status']):
                        evaluations.append([i, j, 2])
                        continue

            else: # Спаны находятся в разных предложениях
                if first_span_feature == second_span_feature: # Спаны одного типа
                    if same_meanings_spans(first_span, second_span, spans_info):
                        evaluations.append([i, j, 1])
                        continue

    return evaluations

def same_meanings_spans(first_span, second_span, spans_info):
    # Определяет, совпадают ли значения спанов

    first_span_info = spans_info.get(first_span)
    first_span_info_lex = first_span_info.get('list_lex')

    second_span_info = spans_info.get(second_span)
    second_span_info_lex = second_span_info.get('list_lex')

    first_span_info_lex_len = len(first_span_info_lex)

    if first_span_info_lex_len != len(second_span_info_lex):
        return False

    for i in range(first_span_info_lex_len):
        if first_span_info_lex[i] != second_span_info_lex[i]:
            return False

    return True

def same_case_numeric(first_span, second_span, spans_info):
    # Определяет, совпадает ли у спанов падеж и число

    first_span_info = spans_info.get(first_span)
    first_span_info_case = first_span_info.get('case')

    second_span_info = spans_info.get(second_span)
    second_span_info_case = second_span_info.get('case')

    if np.dot(first_span_info_case, second_span_info_case) == 0:
        return False

    first_span_info_numeric = first_span_info.get('numeric')
    second_span_info_numeric = second_span_info.get('numeric')

    if np.dot(first_span_info_numeric, second_span_info_numeric) == 0:
        return False

    return True

def subjective_case(span, spans_info):
    # Определяет, находится ли спан в именительном падеже

    span_info = spans_info.get(span)
    span_info_case = span_info.get('case')
    if span_info_case[0] > 0:
        return True

    return False

def form_list_chain_spans(spans, evaluations):
    # Формирует список цепочек спанов

    list_chain_spans = []
    for span in spans:
        list_chain_spans.append([(span[0], span[1], span[2])])

    # form_list_chain_spans_recursion(list_chain_spans, spans, evaluations)

    return list_chain_spans

# def form_list_chain_spans_recursion(list_chain_spans, spans, evaluations):

    # max_evaluations = 0
    # for evaluation in evaluations:
    #     max_evaluations = max(max_evaluations, evaluation[2])
    #
    # if max_evaluations == 0:
    #     return

    # for evaluation in evaluations:
    #     if evaluation[2] == max_evaluations:


