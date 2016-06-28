import mprorp.analyzer.db as db

# keys - fact fields in tomita, values - entity class
fact_entities = {'Person': 'person'}


def convert_tomita_result_to_markup(doc_id, grammars, markup_name='another markup from tomita facts', entity=None, new_status=0):

    if entity is None:
        entity = '0057375a-8242-1c6d-bf64-d5cb5a7ad7dd'
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
    db.put_markup(doc_id, markup_name, classes.keys(), '20', refs, 500)
    # db.put_references(doc_id, markup_id, refs, new_status)

