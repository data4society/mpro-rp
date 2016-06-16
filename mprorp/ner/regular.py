from mprorp.ner.tomita_to_markup import convert_tomita_result_to_markup


def regular_entities(doc_id):
    convert_tomita_result_to_markup(doc_id, ['person.cxx'])