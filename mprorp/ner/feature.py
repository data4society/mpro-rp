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
        db.put_ner_feature(doc_id, gaz_id, values, ner_feature_types['gazetteer'])

