import mprorp.analyzer.db as db
import mprorp.analyzer.rubrucator as rb

#set_id = "1dcc4dc5-a706-4e61-8b37-26b5fd554145"    # Свобода слова 10
rubric_id = '693a9b39-cb8e-4525-9333-1dadcda7c34e' # Свобода собраний

set_id = "7fc5e799-2fa4-40ce-82cd-2793b6889002" # Свобода слова 100

#for doc_id in db.get_set_docs(set_id):
#    print(doc_id)
#    morpho_doc(doc_id)
#    lemmas_freq_doc(doc_id)

#idf_object_features_set(set_id)


rb.learning_rubric_model(set_id, rubric_id)

for doc_id in db.get_set_docs(set_id):
    rb.spot_doc_rubrics(doc_id, {rubric_id: None})