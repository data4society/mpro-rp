"""functions for creating NER features: tomita, gazetteer, morpho, ect."""

import mprorp.analyzer.db as db
import re
import mprorp.ner.morpho_to_vec as morpho_to_vec
import numpy as np
import logging as log

ner_feature_types = {'embedding': 1, 'gazetteer': 2, 'tomita': 3, 'morpho': 4, 'answer': 5, 'OpenCorpora': 6,
                     'Capital': 7,
                     'name_answers': 11,            'name_predictions': 21,
                     'oc_class_person_answers': 12, 'oc_class_person_predictions': 22,
                     'oc_class_org_answers': 13,    'oc_class_org_predictions': 23,
                     'oc_class_loc_answers': 14,    'oc_class_loc_predictions': 24,
                     'loc_answers': 15, 'loc_predictions': 25}

def part_of_speech(gr):
    gr = re.findall('^\w*', gr)
    if len(gr) > 0:
        return gr[0]
    else:
        return ''


def create_gazetteer_feature(doc_id, gaz_id):
    """create gazetteer feature"""
    # create in db gazetteer feature
    # read morpho
    morpho = db.get_morpho(doc_id)
    # read gazetteer
    gazetteer = db.get_gazetteer(gaz_id)
    # for each lemma of each word of doc look for lemma in gazetteer
    values = []
    for element in morpho:
        # if element is word
        if element.get('word_index', -1) != -1:
            analysis = element.get('analysis', [])
            amount = 0
            for l in analysis:
                weight = l.get('wt', 1)
                lemma = l.get('lex', element.get('text', ''))
                if lemma in gazetteer:
                    amount += weight
            if amount > 0:
                # print(amount, element)
                values.append({'word_index': element['word_index'],
                               'sentence_index': element['sentence_index'],
                               'value': [amount]})
    if len(values) > 0:
        # print(values)
        db.put_ner_feature(doc_id, values, ner_feature_types['gazetteer'], gaz_id)


def stronger_value(old_value, value):
    """choose one value from two"""
    priority = {'B': 2, 'I': 4, 'E': 3, 'S': 1}
    if old_value is None:
        return value
    if old_value[1] == value[1]:  # same B I E S
        return value
    elif priority(old_value[1]) > priority(value[1]):
        return value
    else:
        return old_value


def create_tomita_feature2(doc_id, feature_grammars):
    """wrap for create_tomita_feature"""
    db.doc_apply(doc_id, create_tomita_feature, feature_grammars)


def create_tomita_feature(doc, feature_grammars, session=None, commit_session=True):
    """count tomita features - lemmas coordinate using symbol coordinates """
    doc_id = str(doc.doc_id)
    results = db.get_tomita_results(doc_id, feature_grammars, session)
    morpho = doc.morpho
    values = []
    for result in results:
        # result - dict with keys like '15:22' and values like 'person' - tomita fact
        for i in result:
            # print(i)
            offsets = [int(j) for j in i.split(':')]
            offsets[1] += -1
            # find word with offsets
            # [begin, inside, end, single]
            for element in morpho:
                value = None
                if 'start_offset' in element.keys():
                    if element['start_offset'] == offsets[0]:
                        if element['end_offset'] == offsets[1]:
                            # single
                            value = [0, 0, 0, 1]
                            # print(element['text'])
                        elif element['end_offset'] < offsets[1]:
                            # begin
                            value = [1, 0, 0, 0]
                            # print(element['text'])
                        else:
                            # error
                            print('error: ' + doc_id + ' word: "' + element['text'] + '" morpho:', element['start_offset'], ':', element[
                                'end_offset'], ' tomita: ', offsets)
                    elif element['start_offset'] > offsets[0]:
                        if element['end_offset'] == offsets[1]:
                            # end
                            value = [0, 0, 1, 0]
                            print(element['text'])
                        elif element['end_offset'] < offsets[1]:
                            # inside
                            value = [0, 1, 0, 0]
                            print(element['text'])
                        else:
                            # word past offsets
                            break
                    else:
                        if element['end_offset'] >= offsets[0]:
                            # error
                            print('error: ' + doc_id + ' word: "' + element['text'] + '" morpho:', element['start_offset'], ':', element[
                                'end_offset'], ' tomita: ', offsets)
                if not (value is None):
                    values.append({'word_index': element['word_index'],
                                   'sentence_index': element['sentence_index'],
                                   'value': value, 'feature': result[i]})
                    # if (element['word_index'] == 23) and (element['sentence_index'] == 0):
                    print(offsets, result[i], element['word_index'], element['sentence_index'])
    if len(values) > 0:
        # print(values)
        db.put_ner_feature(doc_id, values, ner_feature_types['tomita'], session=session, commit_session=commit_session)


def print_tomita_result2(doc_id, feature_grammars):
    """wrap for print_tomita_result"""
    db.doc_apply(doc_id, print_tomita_result, feature_grammars)


def print_tomita_result(doc, feature_grammars):
    """print tomita results - symbol coordinates from db"""
    doc_id = doc.doc_id
    results = db.get_tomita_results(doc_id, feature_grammars)
    mytext = (doc.stripped).replace('\n','')

    for result in results:
        # result - dict with keys like '15:22' and values like 'person' - tomita fact
        for i in result:
            print(i, result[i])
            offsets = [int(j) for j in i.split(':')]
            print(mytext[offsets[0]:offsets[1]])


def create_embedding_feature2(doc_id):
    """wrap for create_embedding_feature"""
    db.doc_apply(doc_id, create_embedding_feature)


def create_embedding_feature(doc, session=None, commit_session=True):
    """create lemmas to look for in embedding"""
    doc_id = doc.doc_id
    # morpho = db.get_morpho(doc_id)
    morpho = doc.morpho
    values = []
    for element in morpho:
        if element.get('word_index', -1) != -1:
            analysis = element.get('analysis', [])
            feats = {}
            for l in analysis:
                weight = l.get('wt', 1)
                lemma = l.get('lex', '')
                pos = part_of_speech(l.get('gr', ''))
                if (len(lemma) > 0) & (len(pos) > 0):
                    feats[lemma + '_' + pos] = feats.get(lemma + '_' + pos, 0) + weight
            if len(feats) == 0:
                text = element.get('text', '').strip()
                if len(text) > 0:
                    feats[text] = 1
            if len(feats) > 0:
                values.append({'word_index': element['word_index'],
                               'sentence_index': element['sentence_index'],
                               'value': feats})
    if len(values) > 0:
        # print(values)
        db.put_ner_feature(doc_id, values, ner_feature_types['embedding'], 'embedding', session, commit_session)


def create_morpho_feature2(doc_id):
    """wrap for create_morpho_feature"""
    db.doc_apply(doc_id, create_morpho_feature)


def create_morpho_feature(doc, session=None, commit_session=True):
    """create feature for NER from morpho features"""
    doc_id = doc.doc_id
    # morpho = db.get_morpho(doc_id)
    morpho = doc.morpho
    values = []
    for element in morpho:
        if element.get('word_index', -1) != -1:
            analysis = element.get('analysis', [])
            res = np.zeros(morpho_to_vec.vec_len)
            for analyse in analysis:
                # if analyse['wt'] < delta_wt:
                #     continue
                # print(analyse['wt'], analyse['gr'])
                vectors = morpho_to_vec.analyze(analyse['gr'])
                len_vectors = len(vectors)
                for vec in vectors:
                    delta = (analyse['wt'] / len_vectors)
                    res += delta * vec
            values.append({'word_index': element['word_index'],
                           'sentence_index': element['sentence_index'],
                           'value': res.tolist()})
    if len(values) > 0:
        # print(values)
        db.put_ner_feature(doc_id, values, ner_feature_types['morpho'], 'morpho', session, commit_session)


def create_capital_feature2(doc_id):
    """wrap for create_capital_feature"""
    db.doc_apply(doc_id, create_capital_feature)


def create_capital_feature(doc, session=None, commit_session=True):
    """create feature for NER from capital features"""
    doc_id = doc.doc_id
    values = []
    morpho = doc.morpho
    for element in morpho:
        if element.get('word_index', -1) != -1:
            text = element.get('text', '').strip()
            if text == '':
                values.append({'word_index': element['word_index'],
                               'sentence_index': element['sentence_index'],
                               'value': [0, 0]})
            else:
                values.append({'word_index': element['word_index'],
                               'sentence_index': element['sentence_index'],
                               'value': [1 if text[0].isupper() else 0, 0 if len(text) == 1 or text[1:].islower() else 1]})
    if len(values) > 0:
        db.put_ner_feature(doc_id, values, ner_feature_types['Capital'], 'Capital', session, commit_session)

