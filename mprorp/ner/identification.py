import mprorp.analyzer.db as db
import mprorp.ner.feature as feature

def identification_for_doc_id (doc_id):

    feature_type = feature.ner_feature_types['OpenCorpora']

    features = ['oc_feature_last_name', 'oc_feature_first_name', 'oc_feature_middle_name', 'oc_feature_nickname',
                'oc_feature_foreign_name', 'oc_feature_post', 'oc_feature_role', 'oc_feature_status']

    doc_properties = db.get_ner_feature_for_features(doc_id, feature_type, features)
    # doc_properties = [(0, 23, 'oc_feature_status'), (0, 24, 'oc_feature_status'), (1, 0, 'oc_feature_status'),
    #                   (2, 3, 'oc_feature_status'), (2, 4, 'oc_feature_status'), (2, 4, 'oc_feature_last_name'),
    #                   (2, 5, 'oc_feature_status'), (2, 5, 'oc_feature_first_name'),
    #                   (4, 0, 'oc_feature_role'), (4, 1, 'oc_feature_status'), (4, 1, 'oc_feature_role'),
    #                   (4, 2, 'oc_feature_role'), (4, 2, 'oc_feature_status')]
    print(doc_properties)

    spans_list = []
    for i in range(len(doc_properties)):
        doc_property = doc_properties[i]
        find = False
        for span in spans_list:
            if (span[0] == doc_property[0]) and (span[2] + 1 == doc_property[1]) and span[3] == doc_property[2]:
                span[2] = span[2] + 1
                find = True
        if not find:
            spans_list.append([doc_property[0], doc_property[1], doc_property[1], doc_property[2]])
    spans = tuple(spans_list)
    print(spans)

    evaluations = []
    spans_len = len(spans)

    i = -1
    while i < spans_len - 2:

        i += 1
        first_span = spans[i]

        j = i
        while j < spans_len - 1:

            j += 1
            second_span = spans[j]

            #вложенные спаны
            if first_span[0] == second_span[0] and(
                (first_span[1] >= second_span[1] and first_span[1] <= second_span[2] and
                 first_span[2] >= second_span[1] and first_span[2] <= second_span[2]) or (
                 second_span[1] >= first_span[1] and second_span[1] <= first_span[2] and
                 second_span[2] >= first_span[1] and second_span[2] <= first_span[2])):

                evaluations.append((i, j, -1))
                continue

            if first_span[0] == second_span[0] and first_span[2] + 1 == second_span[1]:

                if (first_span[3] == 'oc_feature_last_name' and second_span[3] == 'oc_feature_first_name' or
                    first_span[3] == 'oc_feature_first_name' and second_span[3] == 'oc_feature_last_name' or
                    first_span[3] == 'oc_feature_first_name' and second_span[3] == 'oc_feature_middle_name'):

                    evaluations.append((i, j, 5))
                    continue

                if (first_span[3] in ['oc_feature_role', 'oc_feature_post', 'oc_feature_status'] and
                        second_span[3] in ['oc_feature_first_name', 'oc_feature_last_name', 'oc_feature_foreign_name', 'oc_feature_nickname']):

                    evaluations.append((i, j, 4))
                    continue

            if first_span[0] == second_span[0] and j == i + 1:

                if (first_span[3] in ['oc_feature_role', 'oc_feature_post', 'oc_feature_status']
                    and second_span[3] in ['oc_feature_first_name', 'oc_feature_last_name', 'oc_feature_middle_name',
                                           'oc_feature_foreign_name', 'oc_feature_nickname']):

                    evaluations.append((i, j, 2))
                    continue

                if (first_span[3] in ['oc_feature_first_name', 'oc_feature_last_name', 'oc_feature_middle_name',
                                      'oc_feature_foreign_name', 'oc_feature_nickname']
                    and second_span[3] in ['oc_feature_role', 'oc_feature_post', 'oc_feature_status']):

                    evaluations.append((i, j, 2))
                    continue






    print(evaluations)





