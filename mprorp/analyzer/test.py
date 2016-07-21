import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb
import mprorp.ner.feature as feature
import mprorp.ner.identification as id

# rubric_id = u'd2cf7a5f-f2a7-4e2b-9d3f-fc20ea6504da' # Свобода собраний
# rubric_id = u'76819d19-d3f7-43f1-bc7f-b10ec5a2e2cc' # ОВД-Инфо
# rubric_id = u'6b11126a-5025-454a-bc27-f87f41cb1f09' # Политпрессинг

# set_id = u'f23449f6-08cd-463b-8c90-95480735c4f7' # Свобода слова 10
# test_set_id = u'f23449f6-08cd-463b-8c90-95480735c4f7' # Свобода слова 10
# set_id = u'eb082527-ac1a-4757-a6ea-087d3b277fbc'    # Свобода слова 100#
# set_id = u'0c2bfd6b-2e02-4ca2-9e57-f7506c025dbc' # Все новости
# set_id = u'404f1c89-53bd-4313-842d-d4a417c88d67'   # ОИ 1000 (500:500)
# test_set_id = u'a18bc334-0332-4897-a00e-0bd916290f95'  # ОИ 8000 (4000:4000)


# counter = 0
# for doc_id in db.get_set_docs(set_id):
#     print(counter, doc_id)
#     counter += 1
#     rb.morpho_doc2(doc_id)
#     rb.lemmas_freq_doc2(doc_id)
# # #
# for doc_id in db.get_set_docs(test_set_id):
#     print(counter, doc_id)
#     counter += 1
#     rb.morpho_doc2(doc_id)
#     rb.lemmas_freq_doc2(doc_id)
#
#
# rb.idf_object_features_set(set_id)
# print('start learning')
# rb.learning_rubric_model(set_id, rubric_id)
#
# print('start spot...')
# # for doc_id in db.get_set_docs(set_id):
# #     rb.spot_doc_rubrics2(doc_id, {rubric_id: None})
#
#
# rb.spot_test_set_rubric(test_set_id, rubric_id)
# #
# model_id = db.get_model(rubric_id, set_id)["model_id"]
# result = rb.f1_score(model_id, test_set_id, rubric_id)
# print(result)

# print(rb.probabilities_score(model_id, test_set_id, rubric_id))

# doc_id = u'000e82b8-6ea7-41f4-adc6-bc688fbbeeb6' # 9556b091-b550-4489-9768-1690485fa664
# doc_id = u'add1dd0c-3004-49db-adeb-d841c5d8a9f7'

# rb.spot_doc_rubrics2(doc_id, rb.rubrics_for_regular)
# rb.lemmas_freq_doc2(doc_id)

settings = {'features': {'oc_span_last_name': 'oc_feature_last_name',
            'oc_span_first_name': 'oc_feature_first_name',
            'oc_span_middle_name': 'oc_feature_middle_name',
            'oc_span_nickname': 'oc_feature_nickname',
            'oc_span_foreign_name': 'oc_feature_foreign_name',
            'oc_span_post': 'oc_feature_post',
            'oc_span_role': 'oc_feature_role',
            'oc_span_status': 'oc_feature_status'},
            'consider_right_symbol': False}

# doc_id = 'eadd9485-7d29-69fd-cb0d-b96cf2153ab2'
# doc_id = '45807db3-27ad-47aa-0ae9-2c177ceabd2b'
# doc_id = 'd49ad82c-4a0a-eadb-d27d-2af079e5451c'
# doc_id = 'c05d60f4-1985-2402-487b-709c4d9c6dd7'
doc_id = 'b6020e2f-bad3-ceb2-449e-f28f0ddaa724'
# doc_id = '192f9948-3ce5-fc7e-b485-b5fbfa8465db'
# doc_id = '0d9b0aab-45ca-3974-5f4e-34afabd8183c'
# rb.morpho_doc2(doc_id)

doc_stripped = db.get_doc(doc_id)
print(doc_stripped)

new_status = 0 # Какой тут нужен статус
feature.create_answers_feature_for_doc(doc_id, '30', settings, new_status)

id.identification_for_doc_id(doc_id)