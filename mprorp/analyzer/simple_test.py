import mprorp.analyzer.rubricator as rb

set = [
    '3224687f-9594-4b91-a5ff-2a11856fb71c', # "Письмо Маши Васе"
    'd70080f6-f729-4ec7-9729-5801eac295fb', # "Первый документ Пети"
    '30fb4b89-d408-4467-ba22-09795d8919d6', # "Первое письмо Маши"
    '5cdd8ea1-d0d0-48b5-8a22-d4f3b2042cf9', #  "Второй документ Маши"
    '566410a4-e1a6-4ee8-bec7-42df45ee6f40', #  "Первый документ Васи"
    'a0217805-6897-42b1-be40-52891c9da86a',# "Второй документ Пети"
    "ddcc4166-79f0-4eb0-acb6-fe19b866e15a",# "Первое письмо Пети"
    "844663a5-6aa7-407d-8e7a-cc3d3acf7e14",# "Первое письмо Васи"
    "5f87c1cc-1de3-4b9d-9a37-329f0e42ce32",# "Первый документ Маши"
    "f9a76f65-058e-4510-8d17-bd6595cd8404" # "Письмо Маши Пете"
    ]
# set_id = db.put_training_set(set)
set_id = '420d4561-d78d-40e3-b769-778d9b070076'
docs_id = []
# for id in set:
#     docs_id.append(select(Document.doc_id, Document.doc_id == id).fetchone()[0])
# set_id = db.put_training_set(docs_id)

rubrics_id = ['6816ab38-14fe-4d86-9b34-5608274d20c2', # 'Маша',
              '6ce16076-dac0-4500-a525-2aded662f4f3', # :'Первые',
              '87e687c1-87a9-46ed-a4db-fdb1365d6244'  #:'Письма'}
              ]

# # маша
# insert(DocumentRubric(doc_id = set[0],rubric_id = rubrics_id[0]))
# insert(DocumentRubric(doc_id = set[2],rubric_id = rubrics_id[0]))
# insert(DocumentRubric(doc_id = set[3],rubric_id = rubrics_id[0]))
# insert(DocumentRubric(doc_id = set[8],rubric_id = rubrics_id[0]))
# insert(DocumentRubric(doc_id = set[9],rubric_id = rubrics_id[0]))
# # Первые
# insert(DocumentRubric(doc_id = set[1],rubric_id = rubrics_id[1]))
# insert(DocumentRubric(doc_id = set[2],rubric_id = rubrics_id[1]))
# insert(DocumentRubric(doc_id = set[4],rubric_id = rubrics_id[1]))
# insert(DocumentRubric(doc_id = set[6],rubric_id = rubrics_id[1]))
# insert(DocumentRubric(doc_id = set[7],rubric_id = rubrics_id[1]))
# insert(DocumentRubric(doc_id = set[8],rubric_id = rubrics_id[1]))
# # Письма
# insert(DocumentRubric(doc_id = set[0],rubric_id = rubrics_id[2]))
# insert(DocumentRubric(doc_id = set[2],rubric_id = rubrics_id[2]))
# insert(DocumentRubric(doc_id = set[6],rubric_id = rubrics_id[2]))
# insert(DocumentRubric(doc_id = set[7],rubric_id = rubrics_id[2]))
# insert(DocumentRubric(doc_id = set[9],rubric_id = rubrics_id[2]))

# for doc_id in set:
#    print(doc_id)
#    rb.morpho_doc(doc_id)
#    rb.lemmas_freq_doc(doc_id)

rb.idf_object_features_set(set_id)
rb.learning_rubric_model(set_id, rubrics_id[2])

for doc_id in set:
    rb.spot_doc_rubrics(doc_id, {rubrics_id[2]: None})