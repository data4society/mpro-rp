import mprorp.analyzer.db as db
import mprorp.ner.feature as feature
import mprorp.ner.morpho_to_vec as morpho_to_vec
import numpy as np
import logging as log

settings = {'features': {'oc_span_last_name': 'oc_feature_last_name',
                         'oc_span_first_name': 'oc_feature_first_name',
                         'oc_span_middle_name': 'oc_feature_middle_name',
                         'oc_span_nickname': 'oc_feature_nickname',
                         'oc_span_foreign_name': 'oc_feature_foreign_name',
                         'oc_span_post': 'oc_feature_post',
                         'oc_span_role': 'oc_feature_role',
                         'oc_span_status': 'oc_feature_status'},
            'markup_type': '62',
            'consider_right_symbol': False,
            'entity_class': 'person',
            'put_markup_references': True,
            'put_documents': True}


def create_answers_feature_for_doc(doc, entity_class='oc_class_person', session=None, commit_session=True, verbose=False):

    features = settings.get('features')
    consider_right_symbol = settings.get('consider_right_symbol')

    # let find markup for entity_class
    markup_id = db.get_markup_for_doc_and_class(doc_id=doc.doc_id,entity_class=entity_class,session=session)

    if entity_class == 'oc_class_person':
        references = db.get_references_for_doc(markup_id, session)
        morpho = doc.morpho

        values = {}

        # previous_ref = None
        # word_list_all = []
        sent_dict = {}
        if verbose:
            sent_print = {}
            for element in morpho:

                if 'sentence_index' in element:
                    if element['sentence_index'] not in sent_print:
                        sent_print[element['sentence_index']] = ""
                    sent_print[element['sentence_index']] += element.get("text", "") + " "

        for ref in references:

            start_ref = ref[0]
            end_ref = ref[1]
            ref_class = ref[2]
            # if verbose:
            #     print('coordinates: ', start_ref, end_ref)

            ref_class_value = features.get(ref_class)
            #
            # word_list = []
            for element in morpho:

                value = None
                if 'start_offset2' in element.keys():

                    if element['start_offset2'] == start_ref:

                        if (consider_right_symbol and element['end_offset2'] <= end_ref) or (
                                not consider_right_symbol and element['end_offset2'] < end_ref):

                            value = ref_class_value
                        else:
                            # error
                            log.info(
                                'error: word ' + element['text'] + ' ' + str(element['start_offset2']) + ':' +
                                str(element['end_offset2']) + ' refs: ' + str(ref))
                            if verbose:
                                print('error: word ', element['text'], ' ', str(element['start_offset2']), ':', str(
                                    element['end_offset2']), ' refs: ', str(ref))

                    elif element['start_offset2'] > start_ref:

                        if (consider_right_symbol and element['end_offset2'] <= end_ref) or (
                                        not consider_right_symbol and element['end_offset2'] < end_ref):

                            value = ref_class_value
                        else:
                            break

                    else:

                        if element['end_offset2'] >= start_ref:
                            # error
                            log.info(
                                'error: word ' + element['text'] + ' ' + str(element['start_offset2']) + ':' +
                                str(element['end_offset2']) + ' refs: ' + str(ref))
                            if verbose:
                                print('error: word ', element['text'], ' ', str(element['start_offset2']), ':', str(
                                    element['end_offset2']), ' refs: ', str(ref))

                if not (value is None):
                    if element['sentence_index'] not in sent_dict:
                        sent_dict[element['sentence_index']] = {}
                    sent_dict[element['sentence_index']][element['word_index']] = value

                    # word_list.append((element['sentence_index'], element['word_index']))
                    # word_list_all.append((element['sentence_index'], element['word_index']))
                    values[(element['sentence_index'], element['word_index'], value)] = [1]
                    # if verbose:
                    #     print(element['text'], value)

            # word_list_len = len(word_list)

        for sent_index in sent_dict:
            if verbose:
                print(sent_index, sent_print[sent_index])

            words = sent_dict[sent_index]
            word_indexes = list(words.keys())
            word_indexes.sort()
            prev_person_index = -10
            prev_name_index = -10
            prev_prs_index = -10
            person_chain = []
            name_chain = []
            prs_chain = []
            for word_ind in word_indexes:
                cur_value = None
                if words[word_ind] in ['oc_feature_last_name', 'oc_feature_first_name', 'oc_feature_middle_name',
                                       'oc_feature_nickname', 'oc_feature_foreign_name']:
                    if prev_name_index > 0 and word_ind != prev_name_index + 1:
                        create_values(name_chain, "name", values, verbose)
                    name_chain.append((sent_index, word_ind))
                    prev_name_index = word_ind
                elif words[word_ind] in ['oc_feature_post', 'oc_feature_role', 'oc_feature_status']:
                    if prev_prs_index > 0 and word_ind != prev_prs_index + 1:
                        create_values(prs_chain, "post_role_status", values, verbose)
                    prs_chain.append((sent_index, word_ind))
                    prev_prs_index = word_ind

                if prev_person_index > 0 and word_ind != prev_person_index + 1:
                    create_values(person_chain, "person", values, verbose)
                person_chain.append((sent_index, word_ind))
                prev_person_index = word_ind

            if len(name_chain) > 0:
                create_values(name_chain, "name", values, verbose)
            if len(prs_chain) > 0:
                create_values(prs_chain, "post_role_status", values, verbose)
            if len(person_chain) > 0:
                create_values(person_chain, "person", values, verbose)

            # if not cur_value is None:
            #     values[(word[0], word[1], cur_value)] = [1]
            # i += 1
    else:
        references = db.get_references_for_doc(markup_id, session)
        morpho = doc.morpho

        values = {}

        # previous_ref = None
        # word_list_all = []
        sent_dict = {}
        if verbose:
            sent_print = {}
            for element in morpho:

                if 'sentence_index' in element:
                    if element['sentence_index'] not in sent_print:
                        sent_print[element['sentence_index']] = ""
                    sent_print[element['sentence_index']] += element.get("text", "") + " "

        for ref in references:

            start_ref = ref[0]
            end_ref = ref[1]
            ref_class = ref[2]
            # if verbose:
            #     print('coordinates: ', start_ref, end_ref)

            ref_class_value = features.get(ref_class)
            #
            # word_list = []
            for element in morpho:

                value = None
                if 'start_offset2' in element.keys():

                    if element['start_offset2'] == start_ref:

                        if (consider_right_symbol and element['end_offset2'] <= end_ref) or (
                                    not consider_right_symbol and element['end_offset2'] < end_ref):

                            value = ref_class_value
                        else:
                            # error
                            log.info(
                                'error: word ' + element['text'] + ' ' + str(element['start_offset2']) + ':' +
                                str(element['end_offset2']) + ' refs: ' + str(ref))
                            if verbose:
                                print('error: word ', element['text'], ' ', str(element['start_offset2']), ':', str(
                                    element['end_offset2']), ' refs: ', str(ref))

                    elif element['start_offset2'] > start_ref:

                        if (consider_right_symbol and element['end_offset2'] <= end_ref) or (
                                    not consider_right_symbol and element['end_offset2'] < end_ref):

                            value = ref_class_value
                        else:
                            break

                    else:

                        if element['end_offset2'] >= start_ref:
                            # error
                            log.info(
                                'error: word ' + element['text'] + ' ' + str(element['start_offset2']) + ':' +
                                str(element['end_offset2']) + ' refs: ' + str(ref))
                            if verbose:
                                print('error: word ', element['text'], ' ', str(element['start_offset2']), ':', str(
                                    element['end_offset2']), ' refs: ', str(ref))

                if not (value is None):
                    if element['sentence_index'] not in sent_dict:
                        sent_dict[element['sentence_index']] = {}
                    sent_dict[element['sentence_index']][element['word_index']] = value

                    # word_list.append((element['sentence_index'], element['word_index']))
                    # word_list_all.append((element['sentence_index'], element['word_index']))
                    values[(element['sentence_index'], element['word_index'], value)] = [1]

    if len(values) > 0:
        db.put_ner_feature_dict(doc.doc_id, values, feature.ner_feature_types['OpenCorpora'],
                                 None, session, commit_session)


def create_values(chain, feature_name, values, verbose=False):
    if verbose:
        print(feature_name, chain)
    if len(chain) == 1:
        values[(chain[0][0], chain[0][1], feature_name + "_S")] = [1]
        values[(chain[0][0], chain[0][1], feature_name + "_ES")] = [1]
        values[(chain[0][0], chain[0][1], feature_name + "_BS")] = [1]
    else:
        end_num = len(chain) - 1
        values[(chain[0][0], chain[0][1], feature_name + "_B")] = [1]
        values[(chain[0][0], chain[0][1], feature_name + "_BI")] = [1]
        values[(chain[0][0], chain[0][1], feature_name + "_BS")] = [1]

        values[(chain[end_num][0], chain[end_num][1], feature_name + "_E")] = [1]
        values[(chain[end_num][0], chain[end_num][1], feature_name + "_ES")] = [1]
        values[(chain[end_num][0], chain[end_num][1], feature_name + "_IE")] = [1]
        if end_num > 1:
            for i in range(1, end_num):
                values[(chain[i][0], chain[i][1], feature_name + "_I")] = [1]
                values[(chain[i][0], chain[i][1], feature_name + "_BI")] = [1]
                values[(chain[i][0], chain[i][1], feature_name + "_IE")] = [1]

    chain.clear()


def create_answers_feature_for_doc_2(doc_id):
    db.doc_apply(doc_id,  create_answers_feature_for_doc)


def create_markup(doc, session=None, commit_session=True, verbose=False):

    feature_type = feature.ner_feature_types['OpenCorpora']

    features = ['oc_feature_last_name', 'oc_feature_first_name', 'oc_feature_middle_name', 'oc_feature_nickname',
                'oc_feature_foreign_name', 'oc_feature_post', 'oc_feature_role', 'oc_feature_status']

    # Получим свойства слов документа из БД
    doc_properties = db.get_ner_feature_for_features(doc.doc_id, feature_type, features, session)
    if verbose:
        print('Свойства слов документа:', doc_properties)

    # Сформируем информацию о словах документа (падеж, число, нормальная форма)
    doc_properties_info = form_doc_properties_info(doc, doc_properties, session)
    if verbose:
        for_print = {}
        for i in doc_properties_info:
            for_print[i] = doc_properties_info[i].get('list_lex', [])
        print('Информация о словах документа:', for_print)

    # Сформиреум спаны
    spans = form_spans(doc_properties)
    if verbose:
        print('Спаны:', spans)

    # Сформируем информацию о спанах (падеж, число, нормальная форма)
    spans_info = form_spans_info(spans, doc_properties_info)
    if verbose:
        print('Информация о спанах:', spans_info)

    # Сформируем символьную информацию о спанах
    spans_morpho_info = form_spans_morpho_info(doc, spans)
    if verbose:
        print('Символьная информация о спанах', spans_morpho_info)

    # Сформируем оценки связей спанов
    evaluations, eval_dict = form_evaluations(spans, spans_info)
    if verbose:
        print('Оценки связей:', evaluations)

    # Сформируем список цепочек спанов
    list_chain_spans = form_list_chain_spans(spans, evaluations, eval_dict)
    if verbose:
        print('Цепочки спанов:', list_chain_spans)

    # print(len(spans))
    # print(sum([len(s) for s in list_chain_spans]))

    # Запишем цепочки
    form_entity_for_chain_spans(doc, list_chain_spans, spans_info, spans_morpho_info, session, commit_session)


def create_markup_2(doc_id):
    db.doc_apply(doc_id, create_markup)

def form_doc_properties_info(doc, doc_properties, session):
    # Формирует информацию о словах документа

    doc_morpho = db.get_morpho(doc.doc_id, session)

    doc_properties_info = {}

    for doc_property in doc_properties:

        for element_doc_morpho in doc_morpho:

            sentence_index = element_doc_morpho.get('sentence_index', -1)
            word_index = element_doc_morpho.get('word_index', -1)

            if sentence_index == -1 or word_index == -1:
                continue

            if doc_property[0] == sentence_index and doc_property[1] == word_index:

                analysis = element_doc_morpho.get('analysis')
                if analysis is not None:

                    list_lex = []
                    best_lex = ''
                    best_wt = 0
                    array_case = np.zeros((9))
                    array_numeric = np.zeros((2))

                    len_vectors = 1

                    for analyse in analysis:

                        # Наполняем список лемм
                        current_lex = analyse.get('lex', '')
                        current_wt = analyse.get('wt', 0)
                        if current_lex != '':
                            if current_lex not in list_lex:
                                list_lex.append(current_lex)
                            if current_wt > best_wt:
                                best_lex = current_lex
                                best_wt = current_wt

                        vectors = morpho_to_vec.analyze(analyse['gr'])
                        len_vectors = len(vectors)

                        # Формируем массивы пажедей и чисел
                        for vector in vectors:
                            array_case = array_case + vector[3:12]
                            array_numeric = array_numeric + vector[12:14]

                    array_case /= len_vectors
                    array_numeric /= len_vectors

                    doc_properties_info[doc_property] = {'list_lex': list_lex, 'best_lex': best_lex, 'case': array_case, 'numeric': array_numeric}

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
        best_lex = []
        array_case = np.zeros((9))
        array_numeric = np.zeros((2))

        word_index = span_word_start_index - 1
        while word_index <= span_word_end_index:

            word_index += 1

            doc_property = doc_properties_info.get((span_sentence_index, word_index, span_feature))
            if not doc_property is None:
                list_lex.extend(doc_property.get('list_lex'))
                best_lex.append(doc_property.get('best_lex'))
                array_case += doc_property.get('case')
                array_numeric += doc_property.get('numeric')

        array_case /= (span_word_end_index - span_word_start_index + 1)
        array_numeric /= (span_word_end_index - span_word_start_index + 1)

        spans_info[span] = {'list_lex': list_lex, 'best_lex': best_lex, 'case': array_case, 'numeric': array_numeric}

    return spans_info


def form_spans_morpho_info(doc, spans):

    morpho = doc.morpho

    spans_morpho_info = {}
    for span in spans:
        start_offset = 0
        end_offset = 0
        element_text = ''
        for element in morpho:
            if 'start_offset' in element.keys():
                if element['sentence_index'] == span[0]:
                    if element['word_index'] == span[1]:
                        start_offset = element['start_offset']
                    if element['word_index'] == span[2]:
                        end_offset = element['end_offset']
                    if (element['word_index'] >= span[1]) and (element['word_index'] <= span[2]):
                        element_text += element.get('text','')
        spans_morpho_info[span] = {'start_offset': start_offset, 'end_offset': end_offset, 'text': element_text}

    return spans_morpho_info


def form_evaluations(spans, spans_info):
    # Формирует оценки связей спанов

    spans_len = len(spans)

    evaluations = []
    eval_dict = {}

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
                    evaluations.append([first_span, second_span, -1])
                    eval_dict[(first_span, second_span)] = -1
                    continue

            if first_span_sentence_index == second_span_sentence_index: # Спаны находятся в одном предложении

                # вложенные спаны
                if ((second_span_word_index_start <= first_span_word_index_start <= second_span_word_index_end and
                     second_span_word_index_start <= first_span_word_index_end <= second_span_word_index_end)
                    or
                    (first_span_word_index_start <= second_span_word_index_start <= first_span_word_index_end and
                     first_span_word_index_start <= second_span_word_index_end <= first_span_word_index_end)):

                    evaluations.append([first_span, second_span, -1])
                    eval_dict[(first_span, second_span)] = -1
                    continue

                # Стоящие рядом слова
                if first_span_word_index_end + 1 == second_span_word_index_start:

                    if first_span_feature == 'oc_feature_last_name' and second_span_feature == 'oc_feature_first_name': # Фамилия, Имя

                        if same_case_numeric(first_span, second_span, spans_info): # Одинаковый падеж, число
                            evaluations.append([first_span, second_span, 5])
                            eval_dict[(first_span, second_span)] = 5
                            continue
                        elif subjective_case(first_span, spans_info) or subjective_case(second_span, spans_info): # Фамилия или Имя в им.падеже
                            evaluations.append([first_span, second_span, 3])
                            eval_dict[(first_span, second_span)] = 3
                            continue

                    if first_span_feature == 'oc_feature_first_name' and second_span_feature == 'oc_feature_last_name':  # Имя, Фамилия

                        if same_case_numeric(first_span, second_span, spans_info):  # Одинаковый падеж, число
                            evaluations.append([first_span, second_span, 5])
                            eval_dict[(first_span, second_span)] = 5
                            continue
                        elif subjective_case(first_span, spans_info) or subjective_case(second_span, spans_info): # Фамилия или Имя в им.падеже
                            evaluations.append([first_span, second_span, 3])
                            eval_dict[(first_span, second_span)] = 3
                            continue

                    if first_span_feature == 'oc_feature_first_name' and second_span_feature == 'oc_feature_middle_name':  # Имя, Отчество

                        if same_case_numeric(first_span, second_span, spans_info):  # Одинаковый падеж, число
                            evaluations.append([first_span, second_span, 5])
                            eval_dict[(first_span, second_span)] = 5
                            continue
                        elif subjective_case(first_span, spans_info):  # Имя в им.падеже
                            evaluations.append([first_span, second_span, 3])
                            eval_dict[(first_span, second_span)] = 3
                            continue

                    # Роль, статус, должность перед именем, фамилией, иностр.именем, ником
                    if (first_span_feature in ['oc_feature_role', 'oc_feature_post', 'oc_feature_status'] and
                                second_span_feature in ['oc_feature_first_name', 'oc_feature_last_name',
                                                        'oc_feature_foreign_name', 'oc_feature_nickname']):
                        evaluations.append([first_span, second_span, 4])
                        eval_dict[(first_span, second_span)] = 4
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
                        evaluations.append([first_span, second_span, 2])
                        eval_dict[(first_span, second_span)] = 2
                        continue

            else: # Спаны находятся в разных предложениях
                if first_span_feature == second_span_feature: # Спаны одного типа
                    if same_meanings_spans(first_span, second_span, spans_info):
                        evaluations.append([first_span, second_span, 1])
                        eval_dict[(first_span, second_span)] = 1
                        continue

    return evaluations, eval_dict


def is_sublist(list1, list2):
    result = True
    for l1 in list1:
        if l1 not in list2:
            result = False
            break
    return result


def same_meanings_spans(first_span, second_span, spans_info):
    # Определяет, совпадают ли значения спанов

    first_span_info = spans_info.get(first_span)
    first_span_info_lex = first_span_info.get('list_lex')
    first_span_info_best_lex = first_span_info.get('best_lex')

    second_span_info = spans_info.get(second_span)
    second_span_info_lex = second_span_info.get('list_lex')
    second_span_info_best_lex = second_span_info.get('best_lex')

    return is_sublist(
        first_span_info_best_lex, second_span_info_lex) and is_sublist(
        second_span_info_best_lex, first_span_info_lex)

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


def form_list_chain_spans(spans, evaluations, eval_dict):
    # Формирует список цепочек спанов

    num_span = {}
    i = 1
    for span in spans:
        num_span[span] = i
        i += 1

    list_chain_spans = form_list_chain_spans_recursion(num_span, evaluations, eval_dict)

    print('recursion off')
    return list_chain_spans


def form_list_chain_spans_recursion(num_span, evaluations, eval_dict):
    go_on = True
    eval_number_dict = {}
    for span1 in num_span:
        for span2 in num_span:
            if eval_dict.get((span1, span2), 0) != 0:
                eval_number_dict[(num_span[span1], num_span[span2])] = eval_dict.get((span1, span2), 0)

    while go_on:
        # len_list = len(list_chain_spans)
        # len_eval = len([i for i in evaluations if i[2] > 0])
        # print(len_list)
        # print(len_eval)
        # go_on = False
        max_evaluations = 0
        best_pair = None
        for i in eval_number_dict:
            if eval_number_dict[i] > max_evaluations:
                max_evaluations = eval_number_dict[i]
                best_pair = i

        if max_evaluations > 0:
            print(max_evaluations)

            combine_chains(best_pair[0], best_pair[1], num_span, eval_number_dict)
        else:
            break

    list_chain_spans =[]
    num_chain = {}
    for i in num_span.values():
        num_chain[i] = 0
    for i in num_chain:
        chain = [s for s in num_span if num_span[s] == i]
        list_chain_spans.append(chain)
    return list_chain_spans



def combine_chains(new_num, old_num, num_span, eval_number_dict):

    for i in num_span.values():
        if (i != new_num) and (i != new_num):
            if (eval_number_dict.get((i,new_num), 0) >= 0) and (eval_number_dict.get((new_num, i), 0) >= 0):
                if eval_number_dict.get((i, old_num), 0) == -1:
                    eval_number_dict[(i, new_num)] = -1
                elif eval_number_dict.get((old_num, i), 0) == -1:
                    eval_number_dict[(new_num, i)] = -1
                else:
                    new_eval = max(eval_number_dict.get((i, old_num), 0),
                                   eval_number_dict.get((i, new_num), 0),
                                   eval_number_dict.get((old_num, i), 0),
                                   eval_number_dict.get((new_num, i), 0))
                    eval_number_dict[(i, new_num)] = new_eval
                    eval_number_dict[(new_num, i)] = new_eval
        eval_number_dict[(i, old_num)] = -1
        eval_number_dict[(old_num, i)] = -1

    for i in num_span:
        if num_span[i] == old_num:
            num_span[i] = new_num


    # list_chain_spans_for_one_spans = []
    # list_chain_spans_for_two_spans = []
    #
    # for chain_spans in list_chain_spans:
    #     print('A')
    #     for element_chain_spans in chain_spans:
    #         if element_chain_spans == one_span:
    #             list_chain_spans_for_one_spans.append(chain_spans)
    #         if element_chain_spans == two_span:
    #             list_chain_spans_for_two_spans.append(chain_spans)
    #
    #
    # Flag = True
    # for chain_spans_for_one_spans in list_chain_spans_for_one_spans:
    #     print('B1')
    #     for chain_spans_for_two_spans in list_chain_spans_for_two_spans:
    #         print('B2')
    #         for element_chain_spans_for_one_spans in chain_spans_for_one_spans:
    #             print('B3')
    #             for element_chain_spans_for_two_spans in chain_spans_for_two_spans:
    #                 print('B4')
    #                 if (eval_dict.get((element_chain_spans_for_one_spans,
    #                              element_chain_spans_for_two_spans), 0) < 0) or (eval_dict.get((
    #                             element_chain_spans_for_two_spans, element_chain_spans_for_one_spans), 0) < 0):
    #                     Flag = False
    #                 if not Flag:
    #                     break
    #             if not Flag:
    #                 break
    #         if not Flag:
    #             break
    #     if not Flag:
    #         break
    #
    # if Flag:
    #
    #     i = 0
    #     while i < len(list_chain_spans):
    #         print('C')
    #         if list_chain_spans[i] in list_chain_spans_for_one_spans or list_chain_spans[i] in list_chain_spans_for_two_spans:
    #             list_chain_spans.remove(list_chain_spans[i])
    #         else:
    #             i += 1
    #
    #     for chain_spans_for_one_spans in list_chain_spans_for_one_spans:
    #         for chain_spans_for_two_spans in list_chain_spans_for_two_spans:
    #             print('D')
    #             new_chain = []
    #             for element_chain_spans_for_one_spans in chain_spans_for_one_spans:
    #                 new_chain.append(element_chain_spans_for_one_spans)
    #             for element_chain_spans_for_two_spans in chain_spans_for_two_spans:
    #                 new_chain.append(element_chain_spans_for_two_spans)
    #
    #             list_chain_spans.append(new_chain)


def form_entity_for_chain_spans(doc, list_chain_spans, spans_info, spans_morpho_info, session, commit_session):

    refs = []

    for chain_spans in list_chain_spans:

        name = ''
        first_name = ''
        last_name = ''
        middle_name = ''
        nick_name = ''
        foreign_name = ''
        status = ''
        position = []
        role = []

        for span in chain_spans:

            span_feature = span[3]
            span_info = spans_info.get(span)
            span_info_lex = span_info.get('best_lex')

            if not (span_info_lex is None):
                if span_feature in ['oc_feature_last_name', 'oc_feature_first_name', 'oc_feature_middle_name']:
                    name = ' '.join(span_info_lex)if(name == '')else name + ' ' + ' '.join(span_info_lex)
                if span_feature == 'oc_feature_first_name' and first_name == '':
                    first_name = ' '.join(span_info_lex)
                if span_feature == 'oc_feature_last_name' and last_name == '':
                    last_name = ' '.join(span_info_lex)
                if span_feature == 'oc_feature_middle_name' and middle_name == '':
                    middle_name = ' '.join(span_info_lex)
                if span_feature == 'oc_feature_nickname' and nick_name == '':
                    nick_name = ' '.join(span_info_lex)
                if span_feature == 'oc_feature_foreign_name' and foreign_name == '':
                    foreign_name = ' '.join(span_info_lex)
                if span_feature == 'oc_feature_status':
                    if status == '':
                        status = ' '.join(span_info_lex)
                if span_feature == 'oc_feature_post':
                    position.append(' '.join(span_info_lex))
                if span_feature == 'oc_feature_role':
                    role.append(' '.join(span_info_lex))

        data = {'firstname': first_name,
                'lastname': last_name,
                'middlename': middle_name,
                'nickname': nick_name if nick_name != '' else foreign_name,
                'status': status,
                'position': position,
                'role': role}

        field_count = 0

        dict_search = {}
        if first_name != '':
            dict_search['firstname'] = first_name
            field_count += 1
        if last_name != '':
            dict_search['lastname'] = last_name
            field_count += 1
        if middle_name != '':
            dict_search['middlename'] = middle_name

        if field_count < 2:
            if nick_name != '' or foreign_name != '':
                dict_search['nickname'] = nick_name if nick_name != '' else foreign_name
            elif status != '':
                dict_search['status'] = status
            elif len(position) > 0:
                dict_search['position'] = position
            elif len(role) > 0:
                dict_search['role'] = role

        entity_id = db.get_entity(dict_search, session)
        if entity_id is None:
            entity_id = db.put_entity(name, settings.get('entity_class'), data, session, commit_session)

        if settings.get('put_markup_references', False):

            for span in chain_spans:
                span_morpho_info = spans_morpho_info.get(span)
                if not span_morpho_info is None:
                    start_offset = span_morpho_info.get('start_offset', 0)
                    end_offset = span_morpho_info.get('end_offset', 0)
                    refs.append({'start_offset': start_offset, 'end_offset': end_offset + 1,
                             'len_offset': int(end_offset) - int(start_offset) + 1,
                             'entity': str(entity_id), 'entity_class': settings.get('entity_class')})

    name = 'markup from NER span of person'
    db.put_markup(doc, name, [settings.get('entity_class')], '20', refs, session=session, commit_session=commit_session)





