import mprorp.analyzer.db as db
import re
import mprorp.ner.morpho_to_vec as morpho_to_vec
import numpy as np

ner_feature_types = {'embedding': 1, 'gazetteer': 2, 'tomita': 3, 'morpho': 4}


def part_of_speech(gr):
    gr = re.findall('^\w*', gr)
    if len(gr) > 0:
        return gr[0]
    else:
        return ''


def create_gazetteer_feature(doc_id, gaz_id):
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


def create_tomita_feature(doc_id, feature_grammars, new_status=0):

    results = db.get_tomita_results(doc_id, feature_grammars)
    morpho = db.get_morpho(doc_id)
    values = []
    for result in results:
        # result - dict with keys like '15:22' and values like 'person' - tomita fact
        for i in result:
            print(i)
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
                            print(element['text'])
                        elif element['end_offset'] < offsets[1]:
                            # begin
                            value = [1, 0, 0, 0]
                            print(element['text'])
                        else:
                            # error
                            print('error: word ' + element['text'] + ' ', element['start_offset'], ':', element[
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
                            print('error: word ' + element['text'] + ' ', element['start_offset'], ':', element[
                                'end_offset'], ' tomita: ', offsets)
                if not (value is None):
                    values.append({'word_index': element['word_index'],
                                   'sentence_index': element['sentence_index'],
                                   'value': value, 'feature': result[i]})
    if len(values) > 0:
        # print(values)
        db.put_ner_feature(doc_id, values, ner_feature_types['tomita'], new_status=new_status)


def create_embedding_feature(doc_id, new_status=0):
    morpho = db.get_morpho(doc_id)
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
        db.put_ner_feature(doc_id, values, ner_feature_types['embedding'], 'embedding', new_status=new_status)


def create_morpho_feature(doc_id, new_status=0):
    morpho = db.get_morpho(doc_id)
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
        db.put_ner_feature(doc_id, values, ner_feature_types['morpho'], 'morpho', new_status=new_status)