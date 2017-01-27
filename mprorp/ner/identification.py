import mprorp.analyzer.db as db
import mprorp.ner.feature as feature
import mprorp.ner.morpho_to_vec as morpho_to_vec
import numpy as np
import logging as log
import mprorp.ner.wiki_search as wiki_search
from functools import reduce

settings = {'markup_type': '62',
            'consider_right_symbol': False,
            'entity_class': 'person',
            'put_markup_references': True,
            'put_documents': True}

markup_types = {'oc_class_person': '62',
                'oc_class_org': '51',
                'oc_class_loc': '51'}


def get_ref_from_morpho(reference, morpho, verbose=False):

    consider_right_symbol = settings.get('consider_right_symbol')
    start_ref = reference[0]
    end_ref   = reference[1]
    sent_index = None
    span_chain = []

    for elem in morpho:

        if 'start_offset2' in elem.keys():

            if elem['start_offset2'] == start_ref:

                if (consider_right_symbol and elem['end_offset2'] <= end_ref) or (
                            not consider_right_symbol and elem['end_offset2'] < end_ref) or (
                            elem['end_offset2'] == end_ref) or (
                            elem['end_offset2'] == end_ref + 1):

                    sent_index = elem.get('sentence_index', None)
                    if sent_index is None:
                        print('element: ', elem)
                        print('ref: ', reference)
                        raise Exception('first element in span has no sentence_index')
                    span_chain.append(elem['word_index'])
                else:
                    # error
                    log.info(
                        'error: word ' + elem['text'] + ' ' + str(elem['start_offset2']) + ':' +
                        str(elem['end_offset2']) + ' refs: ' + str(reference))
                    if verbose:
                        print('error: word ', elem['text'], ' ', str(elem['start_offset2']), ':', str(
                            elem['end_offset2']), ' refs: ', str(reference))

            elif elem['start_offset2'] > start_ref:

                if (consider_right_symbol and elem['end_offset2'] <= end_ref) or (
                            not consider_right_symbol and elem['end_offset2'] < end_ref):

                    if sent_index is None:
                        sent_index = elem.get('sentence_index', None)
                    elif sent_index != elem.get('sentence_index', None):
                        break
                        # print('sent_index: ', sent_index)
                        # print('element: ', elem)
                        # print('ref: ', reference)
                        # print('text:')
                        # print(doc.stripped)
                        # raise Exception('different sent_index in span')
                    span_chain.append(elem['word_index'])

                else:
                    break

            else:

                if elem['end_offset2'] >= start_ref:
                    # error
                    log.info(
                        'error: word ' + elem['text'] + ' ' + str(elem['start_offset2']) + ':' +
                        str(elem['end_offset2']) + ' refs: ' + str(reference))
                    if verbose:
                        print('error: word ', elem['text'], ' ', str(elem['start_offset2']), ':', str(
                            elem['end_offset2']), ' refs: ', str(reference))
    return span_chain, sent_index


def create_answers_span_feature_for_doc(doc, spans, markup_type='56', bad_list=set(), ner_feature_name='name_answers',
                                        cl='name', session=None, commit_session=True, verbose=False):
    """Create answers from name/surname """
#
#     # let find markup for entity_class

    markup_id = db.get_markup_by_doc_and_markup_type(doc_id=doc.doc_id, markup_type = markup_type, session=session)

    # if verbose:
    #     print('markup_id: ', markup_id, ' doc_id: ', doc.doc_id)

    references = db.get_references_for_doc(markup_id, session)
    # if verbose:
    #     print('references', len(references))

    morpho = doc.morpho

    sent_dict = {}
    if verbose:
        sent_print = {}
        for element in morpho:

            if 'sentence_index' in element:
                if element['sentence_index'] not in sent_print:
                    sent_print[element['sentence_index']] = ""
                sent_print[element['sentence_index']] += element.get("text", "") + " "

    values = {}

    refs = {}
    minmax_index = {}
    sentence_refs = {}

    # printed = False
    for ref in references:

        ref_class = ref[2]
        # if verbose and not printed:
        #     print(ref_class)
        #     print(spans)
        #     printed = True
        if ref_class not in spans:
                continue
        ref_id = ref[3]
        span_chain, sent_index_ref = get_ref_from_morpho(ref, morpho, verbose=verbose)
        # if verbose:
        #     print('span_chain', span_chain)
        if len(span_chain) > 0:
            if sentence_refs.get(sent_index_ref, None) is None:
                sentence_refs[sent_index_ref] = []
            sentence_refs[sent_index_ref].append(ref_id)
            refs[ref_id] = (sent_index_ref, span_chain, ref_class)
            min_index = span_chain[0]
            max_index = span_chain[0]
            for i in span_chain:
                if i < min_index:
                    min_index = i
                if i > max_index:
                    max_index = i
            minmax_index[ref_id] = {'min': min_index, 'max': max_index}
        else:
            # print('zero chain. dic_id:', str(doc.doc_id), ref)
            bad_list.add(str(doc.doc_id))
    # if verbose:
    #     print('sentence_refs', len(sentence_refs))
    for i in sentence_refs:
        concat_chains_create_values(i, sentence_refs[i], minmax_index, refs, values, cl)

    if len(values) > 0:
        # if verbose:
        #     print(ner_feature_name, feature.ner_feature_types[ner_feature_name])
        db.put_ner_feature_dict(doc.doc_id, values, feature.ner_feature_types[ner_feature_name],
                                None, session, commit_session)
#


def concat_chains_create_values(sent_index, list_refs, minmax_index, refs, values, cl='name', verbose=False):
    first_index = {minmax_index[ref]['min']: ref for ref in list_refs}
    # print(first_index)
    sorted_indexes = list(first_index.keys())
    sorted_indexes.sort()
    chain = [sorted_indexes[0]]
    last_ref = first_index[sorted_indexes[0]]
    last_max = minmax_index[last_ref]['max']
    last_class = refs[last_ref][2]
    for i in range(1,len(sorted_indexes)):
        new_index = sorted_indexes[i]
        new_ref = first_index[new_index]
        new_class = refs[new_ref][2]
        if len(chain) > 0:
            if (new_index == last_max + 1) and (last_class != new_class):
                chain.append(new_index)
                create_values(chain, sent_index, 'name', values, verbose=verbose)
                chain = []
            else:
                create_values(chain, sent_index, 'name', values, verbose=verbose)
                chain = [new_index]
        else:
            chain = [new_index]
        last_class = new_class
        last_max = minmax_index[new_ref]['max']
    if len(chain) > 0:
        create_values(chain, sent_index, cl, values, verbose=verbose)


def create_answers_feature_for_doc(doc, entity_class='oc_class_person', session=None, commit_session=True, verbose=False):
    """Create answers like classname_B, classname_I, ..., classname_BS, classname_IE.
    for example name_BS, name_IE
    """
    # let find markup for entity_class
    main_entity_class = entity_class
    ignore_no_ref_from_mention = False
    if entity_class == 'name':
        main_entity_class = 'oc_class_person'
        ignore_no_ref_from_mention = True

    markup_id = db.get_markup_for_doc_and_class(doc_id=doc.doc_id, entity_class=main_entity_class,
                                                markup_type = markup_types[main_entity_class], session=session)

    if verbose:
        print('markup_id: ', markup_id, ' doc_id: ', doc.doc_id)

    references = db.get_references_for_doc(markup_id, session)
    morpho = doc.morpho

    sent_dict = {}
    if verbose:
        sent_print = {}
        for element in morpho:

            if 'sentence_index' in element:
                if element['sentence_index'] not in sent_print:
                    sent_print[element['sentence_index']] = ""
                sent_print[element['sentence_index']] += element.get("text", "") + " "

    values = {}

    refs = {}

    for ref in references:

        ref_class = ref[2]
        if entity_class == 'name':
            if ref_class not in ['oc_span_first_name', 'oc_span_last_name', 'oc_span_middle_name',
                                 'oc_span_foreign_name', 'oc_span_nickname']:
                continue
        ref_id = ref[3]
        # if verbose:
            # print(ref_id)
        span_chain, sent_index_ref = get_ref_from_morpho(ref, morpho, verbose=verbose)
        # if verbose:
            # print(span_chain)
        if len(span_chain) > 0:
            refs[ref_id] = (sent_index_ref, span_chain, ref_class)
            # if ref_class == 'oc_class_person':
            #     if element['sentence_index'] not in sent_dict:
            #         sent_dict[element['sentence_index']] = {}
            #
            #     for word_index in span_chain:
            #         sent_dict[sent_index_ref][word_index] = ref_class

                # word_list.append((element['sentence_index'], element['word_index']))
                # word_list_all.append((element['sentence_index'], element['word_index']))
                # values[(element['sentence_index'], element['word_index'], value)] = [1]
    # if verbose:
        # print('refs: ', refs)
    # Mentions
    mentions = db.get_mentions(markup_id, main_entity_class, session)
    sent_chains = {}
    for mention in mentions:
        sent_indexes = set()
        # Соберем индексы предложений, которые затронуты mention
        for ref_id in mention[1]:
            ref = refs.get(str(ref_id), None)
            if ref is None:
                if ignore_no_ref_from_mention:
                    continue
                else:
                    print('Error: ref from mention not found')
                    print('    mention: ', mention[0])
                    print('    reference: ', str(ref_id))
                    print('    text: ')
                    print(doc.stripped)
                    print('    morpho: ')
                    print(doc.morpho)
                    raise Exception('Error: ref from mention not found')
            sent_indexes |= {ref[0]}
        # Если оказалось, затронуто более одного предложения - сообщим
        if len(sent_indexes) > 1:
            if verbose:
                print('Mystery: refs from mention have difference sentence indexes')
                print('    mention: ', mention[0])
                # print('    refs: ', list((str(r_id), refs[str(r_id)][0]) for r_id in mention[1]))
                print('    sent_index: ', sent_indexes)
        # Отдельно по каждому предложению:
        # Соберем все участвующие слова из предложения, отсортируем и разобьем на непрерывные цепочки
        for sent_index in sent_indexes:
            words = []
            for ref_id in mention[1]:
                ref = refs.get(str(ref_id), None)
                if ref is None:
                    continue
                if sent_index == ref[0]:
                    words.extend(ref[1])
            if len(words) == 0:
                continue
            words.sort()
            # if verbose:
            #     print(sent_index, words)
            curr_ind = None
            chain = []
            if sent_chains.get(sent_index, None) is None:
                sent_chains[sent_index] = []
            for ind in words:
                if curr_ind is not None:
                    if ind > curr_ind:
                        if ind > curr_ind + 1:
                            sent_chains[sent_index].append(chain)
                            chain = []
                        curr_ind = ind
                        chain.append(ind)
                else:
                    curr_ind = ind
                    chain.append(ind)

            if len(chain) > 0:
                sent_chains[sent_index].append(chain)
    # Eliminate inserted chains and add rest chains to values
    if verbose:
        print(sent_chains)
    for sent_index in sent_chains:
        chains = {}
        for chain in sent_chains[sent_index]:
            if chains.get(chain[0], None) is None:
                chains[chain[0]] = chain
            else:
                if len(chain) > len(chains[chain[0]]):
                    chains[chain[0]] = chain
        # if verbose:
        #     print(sent_index, chains)
        chain_indexes = list(chains.keys())
        chain_indexes.sort()
        old_chain = []
        for first_word in chain_indexes:
            len_old_chain = len(old_chain)
            if len_old_chain > 0:
                if first_word <= old_chain[len_old_chain - 1]: # first_word chain starts before chain ends
                    len_new = len(chains[first_word])
                    if first_word + len_new - 1 > old_chain[len_old_chain - 1]: # i is not inserted in chain
                        print('sentence: ', sent_index)
                        print('chains: ', old_chain, chains[first_word])
                        raise Exception('Crossing chains')
                    # else first_word chain is inserted in old_chain
                else:
                    create_values(old_chain, sent_index, entity_class, values, verbose=verbose)
                    old_chain = chains[first_word]
            else:
                old_chain = chains[first_word]
        if len(old_chain) > 0:
            create_values(old_chain, sent_index, entity_class, values, verbose=verbose)

    if len(values) > 0:
        db.put_ner_feature_dict(doc.doc_id, values, feature.ner_feature_types[entity_class + '_answers'],
                                 None, session, commit_session)


def create_values(chain, sent_index, feature_name, values, verbose=False):
    if verbose:
        print(feature_name, sent_index, chain)
    if len(chain) == 1:
        values[(sent_index, chain[0], feature_name + "_S")] = [1]
        values[(sent_index, chain[0], feature_name + "_ES")] = [1]
        values[(sent_index, chain[0], feature_name + "_BS")] = [1]
    else:
        end_num = len(chain) - 1
        values[(sent_index, chain[0], feature_name + "_B")] = [1]
        values[(sent_index, chain[0], feature_name + "_BI")] = [1]
        values[(sent_index, chain[0], feature_name + "_BS")] = [1]

        values[(sent_index, chain[end_num], feature_name + "_E")] = [1]
        values[(sent_index, chain[end_num], feature_name + "_ES")] = [1]
        values[(sent_index, chain[end_num], feature_name + "_IE")] = [1]
        if end_num > 1:
            for i in range(1, end_num):
                values[(sent_index, chain[i], feature_name + "_I")] = [1]
                values[(sent_index, chain[i], feature_name + "_BI")] = [1]
                values[(sent_index, chain[i], feature_name + "_IE")] = [1]


def create_answers_feature_for_doc_2(doc_id):
    db.doc_apply(doc_id,  create_answers_feature_for_doc)


def create_markup_regular(doc, markup_settings, session=None, commit_session=True, verbose=False):
    settings_list = markup_settings["identification_settings"]
    name = markup_settings["name"]
    markup_type = markup_settings["markup_type"]
    refs = []
    classes = set()
    for ref_settings in settings_list:
        if ref_settings['identification_type'] == 1:
            create_refs(doc, ref_settings, refs, session, commit_session, verbose)
            classes.add(ref_settings['learn_class'])

    if verbose:
        print(refs)
    if len(refs) > 0:
        db.put_markup(doc, name, list(classes), markup_type, refs, session=session, commit_session=commit_session)


def create_markup(doc, session=None, commit_session=True, verbose=False):

    feature_type = feature.ner_feature_types['OpenCorpora']

    features = ['oc_span_last_name', 'oc_span_first_name', 'oc_span_middle_name', 'oc_span_nickname',
                'oc_span_foreign_name', 'oc_span_post', 'oc_span_role', 'oc_span_status']

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


def create_refs(doc, refs_settings, refs, session=None, commit_session=True, verbose=False):

    # feature_type = feature.ner_feature_types['name_predictions']
    # tag_type = ['BS', 'IE'] # ['B', 'I', 'S', 'E'], ['BI', 'ES']
    # learn_class = 'name'

    tag_type = refs_settings['tag_type']
    learn_class = refs_settings['learn_class']
    feature_type = feature.ner_feature_types[learn_class + '_predictions']
    create_new_entities = refs_settings.get('create_new_entities', False)
    create_wiki_entities = refs_settings.get('create_wiki_entities', True)
    # дополнительные условия, которые налагаются при поиске в нашей базе
    add_conditions = refs_settings.get('add_conditions', None)

    features = [learn_class + '_' + i for i in tag_type]

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
        print('Подробно о словах документа:', doc_properties_info)
        print('Информация о словах документа:', for_print)
    # Эта функция должна возвращать нам по каждому упоминанию набор токенов. Затем мы собрав их вместе выясним, как
    # из них являются именами. А затем попытаемся в зависимости от их расположения в конкретных упоминаниях понять, чем
    # являются остальные токены упоминаний.
    # Нет. Собирать токены смысла нет. Т.к. не всегда это слово целиком. Лучше потом полученную метку разрезать по пробелам
    # Но, что следует собрать - это информацию о том, является ли слово Фамилией, Отчеством или Именем по мнению mystem
    mentions, labels, labels_from_text = form_mentions_BS_IE(doc_properties, doc_properties_info, learn_class)
    if verbose:
        print('mentions: ', mentions)
        print('Labels: ', labels)
        print('Labels (text): ', labels_from_text)
    # Сопоставим для всех пар упоминаний попарно все метки
    # Для каждого упоминания получим, упоминания, в которые оно входит, с которыми оно совпадает (хоть по одной метке)
    links = []
    names = []
    for i in range(len(mentions)):
        links.append({'equal': [], 'subs': [], 'parent': [], 'name': labels[i]})
    for i in range(len(mentions) - 1):
        for j in range(i + 1, len(mentions)):
            compare_labels(i, j, [labels[i], labels_from_text[i]], [labels[j], labels_from_text[j]],
                           links[i], links[j], verbose)

    if verbose:
        print('links:', links)
    # В Links:
    # 'equal' - список упоминания, коорые совпали с данным упоминанием хоть по одной метке
    # 'subs' - список дочерних упоминаний
    # 'parent' - список родительских упоминаний
    # 'name' - список наиболее подходящих для наименования меток: берем из текста, если только не оказалось,
    # что вариант не из текста равен варианту из текста в другом упоминании
    # Теоретически могло получиться так, что одно упоминание не имеет родителей, но другое, равное ему - имеет.
    # Плюс отношение равенства ('equal') могло не оказаться отношением эквивалентности.
    # Исправим все это
    local_entities, subclasses, main_class, names = normalize_links(links)
    if verbose:
        print(local_entities, subclasses, names)
    # Здесь local_entities - лист вида [[1,2], [3,6], [4], [5]].
    # Его элементы - это сущности = списки с номерами упоминаний этих сущностей.
    # subclasses - лист содержащий для каждой сущности из local_entities множество дочерних сущностей
    # main_class - булев лист. True означает, что соответствующая сущность не является дочерней для какой-либо другой

    # Соберем все метки по главным классам и найдем классы в нашей базе,
    # либо найдем их в викиданных и создадим соответствующие классы в нашей базе
    # То, что не нашлось ни у нас, ни в викиданных - обработаем ниже
    mentions_id = [None for i in range(len(local_entities))]

    labels_lists = [None for i in range(len(local_entities))]
    for i in range(len(local_entities)):

        if main_class[i]:
            labels_lists[i] = list(reduce(lambda a, x: a | x, [set([labels[j],
                                                                   labels_from_text[j]]) for j in local_entities[i]]))
            # Теперь поищем, что у нас есть по меткам из labels_set - только точное совпадение с одной из меток
            if verbose:
                print('get_entity_by_labels', )
            db_id = db.get_entity_by_labels(labels_lists[i], add_conditions=add_conditions, verbose=verbose)
            if (db_id is None) and create_wiki_entities:
                best_label = None
                # Ищем сущности в викиданных
                found_items = dict()
                for l in labels_lists[i]:
                    if len(l) < 2:
                        # Это инициал, который ни с чем не "склеился"
                        continue
                    # if wiki_search.is_given_name(l):
                    if db.is_name(l):
                        # Это просто имя - такое как
                        # Алексей, Татьяна
                        continue
                    wiki_ids_l = wiki_search.find_human(l)
                    for elem in wiki_ids_l:
                        found_items[elem['id']] = elem
                        best_label = l
                if len(found_items) == 1:
                    wiki_id = list(found_items.keys())[0]
                    ext_data = {'wiki_id': wiki_id}
                    # Раз мы что-то нашли, причем один раз, то метка, по котоой это найдено - точно наилучший вариант имени
                    names[i] = best_label
                    if verbose:
                        print(labels_lists[i])
                    data = None
                    if 'name' in found_items[wiki_id]:
                        data = {'firstname': found_items[wiki_id]['name']}
                    if 'family_name' in found_items[wiki_id]:
                        if data is None:
                            data = dict()
                        data['lastname'] = found_items[wiki_id]['family_name']
                    db_id = db.put_entity(names[i], 'person', data=data, labels=labels_lists[i], external_data=ext_data,
                                          session=session, commit_session=commit_session)
            if db_id is not None:
                mentions_id[i] = db_id
    if verbose:
        print('mentions_id 1:', mentions_id)
    # Те классы, которые не удалось идентифицировать проверим следующим образом:
    # Кажлый токен каждого упоминания, длины больше 1 (чтобы исключить дефисы) проверим на вхождение в другие классы
    # Если окажется, что токены одного упоминания входят в разные классы, то, нужно разбивать упоминание на несколько и
    # формировать заменять соответствующий классы на подклассы.
    # В результате мы дополним mentions новыми упоминаниями, а некоторые старые заменим (обрежем),
    # также мы пополним новыми классами local_entities и новыми отношениями subclasses, т.к. вновь образованные классы
    # по пстроению окажутся подклассами других классов. Также мы выключим для обрезанных (ставших подклассами) классов
    # флаги в main_class
    #
    # ...
    # сделаем это потом.
    # ...
    # будем считать, что все это уже проделано. После этого те классы, которые все же остались в main_class,
    # но еще не имеют mentions_id, нужно занести в БД. Новых main_class еще не появилось,
    # значит можно воспользоваться посчитанным ранее labels_lists[i]

    if create_new_entities:
        # Создадим сущности для всего, что попалось под руку
        for i in range(len(main_class)):
            if main_class[i] and mentions_id[i] is None:
                # data = {'labels': labels_lists[i]}
                fio = names[i].split(' ')
                isname = []
                for count in len(fio):
                    isname.append(db.is_name(fio[count]))
                fio_name = ''
                fio_fam = ''
                if isname[0]:
                    count = 0
                    while (count < len(fio)) and isname[count]:
                        fio_name += fio[count] + ' '
                        count += 1
                    while (count < len(fio)):
                        fio_fam += fio[count] + ' '
                        count += 1
                else:
                    while (count < len(fio)) and not isname[count]:
                        fio_fam += fio[count] + ' '
                        count += 1
                    while (count < len(fio)):
                        fio_name += fio[count] + ' '
                        count += 1

                if verbose:
                    print('data', {'firstname': fio_name, 'lastname': fio_fam})

                mentions_id[i] = db.put_entity(names[i], 'person', data={'firstname': fio_name, 'lastname': fio_fam},
                                               labels=labels_lists[i],
                                               session=session, commit_session=commit_session)

    # Выберем те классы, которые являются подклассом ровно одного класса.
    # Для этого соберем родителей каждого класса
    parents = [[] for i in range(len(local_entities))]
    for i in range(len(subclasses)):
        for j in subclasses[i]:
            parents[j].append(i)
    # В тех случаях, когда родитель у класса один, распространим на него id сущности родительского класса
    if verbose:
        print('parents:', parents)
    for i in range(len(parents)):
        if len(parents[i]) == 1:
            mentions_id[i] = mentions_id[parents[i][0]]
    if verbose:
        print('mentions_id 2:', mentions_id)

    # Классы, которые остались без сущностей - это подклассы двух и более классов.
    # Забудем пока про них, а позже можно будет их отнести к одному из классов
    # по признаку близости расположения в локументе

    # Теперь осталось записать в базу данных markup'ы с найденными и созданными сущностями
    # для этого по каждому упоминанию сформируем символьные координаты
    for i in range(len(mentions_id)):
        if mentions_id[i] is not None:
            start_offset = doc_properties_info[mentions[i][0]]['start_offset']
            end_offset = doc_properties_info[mentions[i][len(mentions[i]) - 1]]['end_offset']
            refs.append({'start_offset': start_offset, 'end_offset': end_offset + 1,
                         'len_offset': end_offset - start_offset + 1,
                         'entity': str(mentions_id[i]), 'entity_class': 'person'})


def normalize_links(links):
    all_equal = set()
    local_entities = []
    names = []
    for i in range(len(links)):
        if i not in all_equal:
            # Новый класс эквивалентности
            equal = set([i])
            add_equal(links, i, equal)
            local_entities.append(equal)
            names_weights = {}
            for s in equal:
                names_weights[links[s]['name']] = names_weights.get(links[s]['name'], 0) + 1
            best_name = ''
            max_weight = 0
            for s in names_weights:
                if max_weight < names_weights[s]:
                    best_name = s
            names.append(best_name)
            all_equal |= equal
    # Теперь соберем для каждого класса все его подчиненные упоминания, всех уровней
    num_classes = len(local_entities)
    subclasses = [set() for i in range(num_classes)]
    # Для каждой пары классов установим, является ли один из них подклассом другого по какой-либо паре упоминаний
    for class_1 in range(num_classes - 1):
        for class_2 in range(class_1 + 1, num_classes):
            if reduce(lambda a, x: a or x, [i in links[j]['subs']
                                    for i in local_entities[class_1] for j in local_entities[class_2]]):
                subclasses[class_2].add(class_1)
            elif reduce(lambda a, x: a or x, [i in links[j]['subs']
                                    for i in local_entities[class_2] for j in local_entities[class_1]]):
                subclasses[class_1].add(class_2)

    # Выберем те классы, которые  не являются подклассами какого-либо другого класса
    main_class = [not reduce(lambda a, x: a or x, [((i in subclasses[j]) and (i != j)) for j in range(num_classes)])
                  for i in range(num_classes)]
    # Перенесем все подклассы подклассов в подклассы
    for i in range(num_classes):
        if main_class[i]:
            final_set = subclasses[i]
            subclasses[i] = set()
            new_set = set()
            while not final_set.issubset(subclasses[i]):
                subclasses[i] |= final_set
                for j in final_set:
                    new_set |= subclasses[j]
                final_set = new_set
                new_set = set()
    # Только теперь очистим подклассы неглавных классов. Сразу нельзя было,
    # т.к. класс может быть подклассом в нескольких классах верхнего уровня
    # Перенесем все подклассы в родительские классы верхнего уровня
    for i in range(num_classes):
        if not main_class[i]:
            subclasses[i] = set()

    return local_entities, subclasses, main_class, names


def add_equal(links, i, equal):
    for j in set(links[i]['equal']).difference(equal):
        equal.add(j)
        add_equal(links, j, equal)


def compare_labels(i, j, labels_i, labels_j,  links_i, links_j, verbose):
    if verbose:
        print('labels:', labels_i, labels_j)
    for count_i in range(len(labels_i)):
        for count_j in range(len(labels_j)):

            if labels_i[count_i] == labels_j[count_j]:
                links_i['equal'].append(j)
                links_j['equal'].append(i)
                if count_i != count_j:
                    links_i['name'] = labels_i[count_i]
                    links_j['name'] = labels_i[count_i]
                    if verbose:
                        print('name: ', labels_i[count_i])
                return

    for label_i in labels_i:
        for label_j in labels_j:
            if label_i.find(label_j) > -1:
                links_i['subs'].append(j)
                links_j['parent'].append(i)
                if verbose:
                    print("links_i['subs']:", links_i['subs'])
                return

            if label_j.find(label_i) > -1:
                links_j['subs'].append(i)
                links_i['parent'].append(j)
                if verbose:
                    print("links_j['subs']:", links_j['subs'])
                return


def create_markup_2(doc_id):
    db.doc_apply(doc_id, create_markup)


def form_doc_properties_info(doc, doc_properties, session):
    # Формирует информацию о словах документа

    doc_morpho = doc.morpho

    doc_properties_info = {}

    for doc_property in doc_properties:
        doc_property_is_found = False

        for element_doc_morpho in doc_morpho:

            sentence_index = element_doc_morpho.get('sentence_index', -1)
            word_index = element_doc_morpho.get('word_index', -1)

            this_is_space = False
            if sentence_index == -1 or word_index == -1:
                this_is_space = True

            if doc_property_is_found:
                doc_properties_info[doc_property]['next_one_is_space'] = this_is_space
                break
            elif doc_property[0] == sentence_index and doc_property[1] == word_index:
                doc_property_is_found = True
                analysis = element_doc_morpho.get('analysis')
                if analysis is None:
                    best_lex = element_doc_morpho.get('text', '')
                    doc_properties_info[doc_property] = {'list_lex': [best_lex], 'best_lex': best_lex, 'text': best_lex}
                else:

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

                    text = element_doc_morpho.get('text', ' ')

                    doc_properties_info[doc_property] = {'list_lex': list_lex, 'best_lex': best_lex,
                                                         'case': array_case, 'numeric': array_numeric,
                                                         'first_supper': text[0].isupper(),
                                                         'all_supper': text.isupper(),
                                                         'start_offset': element_doc_morpho['start_offset'],
                                                         'end_offset': element_doc_morpho['end_offset'],
                                                         'text': text}

    return doc_properties_info


def form_mentions_BS_IE(doc_properties, doc_properties_info, learn_class):
    mentions = []
    labels = []
    texts = []
    # tokens =[]
    # token = []
    mention = []
    label = ''
    last_sent = -1
    last_word = -1
    text = ''

    for word in doc_properties:
        word_label = get_label_from_prop_info(doc_properties_info[word])
        text_label = doc_properties_info[word]['text'] + (' ' if doc_properties_info[word]['next_one_is_space'] else '')
        if word[0] == last_sent and word[1] == last_word + 1 and word[2] == learn_class + '_IE':
            mention.append(word)
            # token.append({'text': text_label, 'word': word_label})
            label = label + word_label
            text = text + text_label
        else:
            if len(mention) != 0:
                mentions.append(mention)
                # tokens.append(token)
                labels.append(label.strip())
                texts.append(text.strip())
            mention = [word]
            # word_label.strip()
            # text_label.strip()
            # token = [{'text': text_label, 'word': word_label}]
            label = word_label
            text = text_label
        last_sent = word[0]
        last_word = word[1]
    if len(mention):
        mentions.append(mention)
        # tokens.append(token)
        labels.append(label.strip())
        texts.append(text.strip())
    return mentions, labels, texts


def get_label_from_prop_info(info):
    first_supper = info.get('first_supper', False)
    all_supper = info.get('all_supper', False)
    label = info.get('best_lex', '')
    if all_supper:
        label = label.upper()
    elif first_supper:
        label = label.capitalize()
    if info.get('next_one_is_space', False):
        return label + ' '
    else:
        return label


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
            if (first_span_feature == second_span_feature and first_span_feature in ['oc_span_last_name',
                                                                                     'oc_span_first_name',
                                                                                     'oc_span_middle_name']):
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

                    if first_span_feature == 'oc_span_last_name' and second_span_feature == 'oc_span_first_name': # Фамилия, Имя

                        if same_case_numeric(first_span, second_span, spans_info): # Одинаковый падеж, число
                            evaluations.append([first_span, second_span, 5])
                            eval_dict[(first_span, second_span)] = 5
                            continue
                        elif subjective_case(first_span, spans_info) or subjective_case(second_span, spans_info): # Фамилия или Имя в им.падеже
                            evaluations.append([first_span, second_span, 3])
                            eval_dict[(first_span, second_span)] = 3
                            continue

                    if first_span_feature == 'oc_span_first_name' and second_span_feature == 'oc_span_last_name':  # Имя, Фамилия

                        if same_case_numeric(first_span, second_span, spans_info):  # Одинаковый падеж, число
                            evaluations.append([first_span, second_span, 5])
                            eval_dict[(first_span, second_span)] = 5
                            continue
                        elif subjective_case(first_span, spans_info) or subjective_case(second_span, spans_info): # Фамилия или Имя в им.падеже
                            evaluations.append([first_span, second_span, 3])
                            eval_dict[(first_span, second_span)] = 3
                            continue

                    if first_span_feature == 'oc_span_first_name' and second_span_feature == 'oc_span_middle_name':  # Имя, Отчество

                        if same_case_numeric(first_span, second_span, spans_info):  # Одинаковый падеж, число
                            evaluations.append([first_span, second_span, 5])
                            eval_dict[(first_span, second_span)] = 5
                            continue
                        elif subjective_case(first_span, spans_info):  # Имя в им.падеже
                            evaluations.append([first_span, second_span, 3])
                            eval_dict[(first_span, second_span)] = 3
                            continue

                    # Роль, статус, должность перед именем, фамилией, иностр.именем, ником
                    if (first_span_feature in ['oc_span_role', 'oc_span_post', 'oc_span_status'] and
                                second_span_feature in ['oc_span_first_name', 'oc_span_last_name',
                                                        'oc_span_foreign_name', 'oc_span_nickname']):
                        evaluations.append([first_span, second_span, 4])
                        eval_dict[(first_span, second_span)] = 4
                        continue

                # Стоящие рядом спаны
                if j == i + 1:

                    # Роль, статус, должность в одном предложении с именем, отчеством, фамилией, иностр.именем, ником
                    if (first_span_feature in ['oc_span_role', 'oc_span_post', 'oc_span_status'] and
                                second_span_feature in ['oc_span_first_name', 'oc_span_last_name',
                                                        'oc_span_middle_name',
                                                        'oc_span_foreign_name', 'oc_span_nickname'] or
                                    first_span_feature in ['oc_span_first_name', 'oc_span_last_name',
                                                           'oc_span_middle_name',
                                                           'oc_span_foreign_name', 'oc_span_nickname'] and
                                    second_span_feature in ['oc_span_role', 'oc_span_post', 'oc_span_status']):
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
                if span_feature in ['oc_span_last_name', 'oc_span_first_name', 'oc_span_middle_name']:
                    name = ' '.join(span_info_lex)if(name == '')else name + ' ' + ' '.join(span_info_lex)
                if span_feature == 'oc_span_first_name' and first_name == '':
                    first_name = ' '.join(span_info_lex)
                if span_feature == 'oc_span_last_name' and last_name == '':
                    last_name = ' '.join(span_info_lex)
                if span_feature == 'oc_span_middle_name' and middle_name == '':
                    middle_name = ' '.join(span_info_lex)
                if span_feature == 'oc_span_nickname' and nick_name == '':
                    nick_name = ' '.join(span_info_lex)
                if span_feature == 'oc_span_foreign_name' and foreign_name == '':
                    foreign_name = ' '.join(span_info_lex)
                if span_feature == 'oc_span_status':
                    if status == '':
                        status = ' '.join(span_info_lex)
                if span_feature == 'oc_span_post':
                    position.append(' '.join(span_info_lex))
                if span_feature == 'oc_span_role':
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





