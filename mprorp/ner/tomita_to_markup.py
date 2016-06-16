import mprorp.analyzer.db as db

# keys - fact fields it tomita, values - entity class
fact_entities = {'Person': 'person'}


def convert_tomita_result_to_markup(doc_id, grammars, markup_name='another markup from tomita facts', entity=None):

    results = db.get_tomita_results(doc_id, grammars)
    print(results)
    classes = {}
    refs = []
    for result in results:
        # result - dict with keys like '15:22' and values like 'person' - tomita fact
        for i in result:
            print(i)
            offsets = i.split(':')
            refs.append({'start_offset': offsets[0], 'end_offset': offsets[1],
                         'entity': entity, 'entity_class': fact_entities[result[i]]})
            classes[fact_entities[result[i]]] = ''
    markup_id = db.put_markup(doc_id, markup_name, classes.keys(), '20', 500)
    db.put_references(markup_id, refs)

