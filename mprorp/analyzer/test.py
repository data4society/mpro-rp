import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb

set_id = u'293035dc-9db0-46b2-9247-f88423bbaef3'    # Свобода слова 100
rubric_id = u'd2cf7a5f-f2a7-4e2b-9d3f-fc20ea6504da' # Свобода собраний

# set_id = u'dc10f916-7f33-4d19-9ba9-0d2e6f24c947' # Свобода слова 10
#
# set_id = u'cd63d6af-f0b2-4bbf-bea2-0b0e2294283d' # Все новости

# counter = 0
# for doc_id in db.get_set_docs(set_id):
#    # print(counter, doc_id)
#    # counter += 1
#    rb.morpho_doc(doc_id)
#    rb.lemmas_freq_doc(doc_id)
# #
rb.idf_object_features_set(set_id)

rb.learning_rubric_model(set_id, rubric_id)
#
# for doc_id in db.get_set_docs(set_id):
#     rb.spot_doc_rubrics(doc_id, {rubric_id: None})
#
# result = rb.f1_score(db.get_model(rubric_id, set_id)["model_id"], set_id, rubric_id)
# print(result)