import mprorp.analyzer.db as db

# keys - fact fields in tomita, values - entity class
fact_entities = {'Person': 'person',
                 'Loc': 'location',
                 'Date': 'date',
                 'Adr': 'address',
                 'Org': 'org',
                 'Norm': 'norm',
                 'Prof': 'prof'}


def convert_tomita_result_to_markup2(doc_id, grammars):
    return db.doc_apply(doc_id, convert_tomita_result_to_markup, grammars)


def convert_tomita_result_to_markup(doc, grammars,
                                    markup_name='another markup from tomita facts',
                                    entity=None, session=None, commit_session=True):

    if entity is None:
        entity = '0057375a-8242-1c6d-bf64-d5cb5a7ad7dd'
    doc_id = doc.doc_id
    results = db.get_tomita_results(doc_id, grammars)
    print(results)
    classes = {}
    refs = []
    for result in results:
        # result - dict with keys like '15:22' and values like 'person' - tomita fact
        for i in result:
            print(i)
            offsets = i.split(':')
            refs.append({'start_offset': int(offsets[0]), 'end_offset': int(offsets[1]),
                         'len_offset':int(offsets[1])-int(offsets[0]),
                         'entity': entity, 'entity_class': fact_entities[result[i]]})
            classes[fact_entities[result[i]]] = ''
    db.put_markup(doc, doc_id, markup_name, classes.keys(), '20', refs, session=session, commit_session=commit_session)
    # db.put_references(doc_id, markup_id, refs, new_status)

