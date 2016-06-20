import mprorp.analyzer.db as db
ner_feature_types = {'embedding': 1, 'gazetteer': 2, 'tomita': 3, 'syntactic_feature_case': 4,
                     'syntactic_feature_plural_singular': 5}


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


def create_tomita_features(doc_id, feature_grammars, new_status=0):

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
                            print('error: word ' + element['text'] + ' ' + element['start_offset'] + ':' + element[
                                'end_offset'] + ' tomita: ' + offsets)
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

