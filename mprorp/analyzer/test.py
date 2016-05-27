import mprorp.analyzer.db as db
import mprorp.analyzer.rubricator as rb

#set_id = "1dcc4dc5-a706-4e61-8b37-26b5fd554145"    # Свобода слова 10
rubric_id = '693a9b39-cb8e-4525-9333-1dadcda7c34e' # Свобода собраний

set_id = "7fc5e799-2fa4-40ce-82cd-2793b6889002" # Свобода слова 100

set_id = 'a28852e0-1a06-43f3-adda-30984c992e0f' # Все новости

counter = 0
for doc_id in db.get_set_docs(set_id):
   print(counter, doc_id)
   counter += 1
   rb.morpho_doc(doc_id)
   rb.lemmas_freq_doc(doc_id)

rb.idf_object_features_set(set_id)


rb.learning_rubric_model(set_id, rubric_id)

for doc_id in db.get_set_docs(set_id):
    rb.spot_doc_rubrics(doc_id, {rubric_id: None})