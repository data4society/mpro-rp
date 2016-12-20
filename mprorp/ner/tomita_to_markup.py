"""function for convert tomita result to markup: symbol to symbol coordinates"""
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
    """wrap for convert_tomita_result_to_markup with local session"""
    return db.doc_apply(doc_id, convert_tomita_result_to_markup, grammars)


def convert_tomita_result_to_markup(doc, grammars,
                                    markup_name='another markup from tomita facts',
                                    entity=None, session=None, commit_session=True, verbose=False):
    if 'ovd.cxx' not in grammars:
        """convert tomita result to markup: symbol to symbol coordinates"""
        default_entity = '0057375a-8242-1c6d-bf64-d5cb5a7ad7dd'
        default_entities = {'location': '20b364e7-a5a9-4202-a8ef-4e5e987191fb',
                            'org': '20b364e7-a5a9-4202-a8ef-4e5e987191fc',
                            'norm': '20b364e7-a5a9-4202-a8ef-4e5e987191fd'}
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
                refs.append({
                    'start_offset': int(offsets[0]), 'end_offset': int(offsets[1]),
                    'len_offset': int(offsets[1]) - int(offsets[0]),
                    'entity': default_entities.get(fact_entities[result[i]],
                                                   default_entity) if entity is None else entity,
                    'entity_class': fact_entities[result[i]]
                })
                classes[fact_entities[result[i]]] = ''
        if verbose:
            print('refs ', refs)
        db.put_markup(doc, markup_name, classes.keys(), '20', refs, new_doc_markup=False, session=session,
                      commit_session=commit_session, verbose=verbose)
    # db.put_references(doc_id, markup_id, refs, new_status)
    else:
        other_grammars = []
        for grammar in grammars:
            if grammar != 'ovd.cxx':
                other_grammars.append(grammar)
        if other_grammars != []:
            default_entity = '0057375a-8242-1c6d-bf64-d5cb5a7ad7dd'
            default_entities = {'location': '20b364e7-a5a9-4202-a8ef-4e5e987191fb',
                                'org': '20b364e7-a5a9-4202-a8ef-4e5e987191fc',
                                'norm': '20b364e7-a5a9-4202-a8ef-4e5e987191fd'}
            doc_id = doc.doc_id
            results = db.get_tomita_results(doc_id, other_grammars)
            print(results)
            classes = {}
            refs = []
            for result in results:
                # result - dict with keys like '15:22' and values like 'person' - tomita fact
                for i in result:
                    print(i)
                    offsets = i.split(':')
                    refs.append({
                        'start_offset': int(offsets[0]), 'end_offset': int(offsets[1]),
                        'len_offset': int(offsets[1]) - int(offsets[0]),
                        'entity': default_entities.get(fact_entities[result[i]],
                                                       default_entity) if entity is None else entity,
                        'entity_class': fact_entities[result[i]]
                    })
                    classes[fact_entities[result[i]]] = ''
            if verbose:
                print('refs ', refs)
            db.put_markup(doc, markup_name, classes.keys(), '20', refs, new_doc_markup=False, session=session,
                          commit_session=commit_session, verbose=verbose)
            # db.put_references(doc_id, markup_id, refs, new_status)
        doc_id = doc.doc_id
        results = db.get_tomita_results(doc_id, ['ovd.cxx'])
        print(results)
        classes = {}
        refs = []
        for result in results:
            # result - dict with keys like '15:22' and values like 'person' - tomita fact
            for i in result:
                print(i)
                offsets = i.split(':')
                refs.append({
                    'start_offset': int(offsets[0]), 'end_offset': int(offsets[1]),
                    'len_offset': int(offsets[1]) - int(offsets[0]),
                    'entity': result[i] if entity is None else entity,
                    'entity_class': 'org'
                })
                classes[result[i]] = ''
        if verbose:
            print('refs ', refs)
        db.put_markup(doc, markup_name, classes.keys(), '20', refs, new_doc_markup=False, session=session,
                      commit_session=commit_session, verbose=verbose)
        # db.put_references(doc_id, markup_id, refs, new_status)
