import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb


# rubric_id = u'd2cf7a5f-f2a7-4e2b-9d3f-fc20ea6504da' # Свобода собраний
rubric_id = u'76819d19-d3f7-43f1-bc7f-b10ec5a2e2cc' # ОВД-Инфо
# rubric_id = u'6b11126a-5025-454a-bc27-f87f41cb1f09' # Политпрессинг

# set_id = u'f23449f6-08cd-463b-8c90-95480735c4f7' # Свобода слова 10
# set_id = u'eb082527-ac1a-4757-a6ea-087d3b277fbc'    # Свобода слова 100#
# set_id = u'0c2bfd6b-2e02-4ca2-9e57-f7506c025dbc' # Все новости
set_id = u'404f1c89-53bd-4313-842d-d4a417c88d67'   # ОИ 1000 (500:500)
test_set_id = u'a18bc334-0332-4897-a00e-0bd916290f95'  # ОИ 8000 (4000:4000)


counter = 0
for doc_id in db.get_set_docs(set_id):
    print(counter, doc_id)
    counter += 1
    rb.morpho_doc(doc_id)
    rb.lemmas_freq_doc(doc_id)
# #
for doc_id in db.get_set_docs(test_set_id):
    print(counter, doc_id)
    counter += 1
    rb.morpho_doc(doc_id)
    rb.lemmas_freq_doc(doc_id)


rb.idf_object_features_set(set_id)
print('start learning')
rb.learning_rubric_model(set_id, rubric_id)

print('start spot...')
# for doc_id in db.get_set_docs(set_id):
#     rb.spot_doc_rubrics(doc_id, {rubric_id: None})


rb.spot_test_set_rubric(test_set_id, rubric_id)
#
model_id = db.get_model(rubric_id, set_id)["model_id"]
result = rb.f1_score(model_id, test_set_id, rubric_id)
print(result)

print(rb.probabilities_score(model_id, test_set_id, rubric_id))
