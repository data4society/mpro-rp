import mprorp.analyzer.rubricator as rb
from mprorp.db.models import *
from mprorp.ner.identification import create_answers_feature_for_doc

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
doc_id = '77ea2e3a-6bce-9622-ca2a-69f2f7de52dc'
session = rb.Driver.db_session()
doc = session.query(Document).filter_by(doc_id=doc_id).first()
doc_text = doc.stripped

rb.mystem_analyzer.start()
# new_morpho = mystem_analyzer.analyze(doc_text)
new_morpho = rb.mystem_analyzer.analyze(doc_text)
print(new_morpho)
exit()
# rb.mystem_analyzer.start()
# new_morpho = mystem_analyzer.analyze(doc_text)
print(doc_text)
# new_morpho = rb.mystem_analyzer.analyze(doc_text)
print(doc.morpho)
doc = session.query(Document).filter_by(doc_id=doc_id).first()

sets = {'oc_class_org': {'train': '78f8c9fb-e385-442e-93b4-aa1a18e952d0',
                         'test': '299c8bd1-4e39-431d-afa9-398b2fb23f69'},
        'oc_class_loc': {'train': '74210e3e-0127-4b21-b4b7-0b55855ca02e',
                         'test': '352df6b5-7659-4f8c-a68d-364400a5f0da'}}
for cl in sets:
    create_answers_feature_for_doc(doc, cl, verbose=True)
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
#    # print(doc_id)
#    rb.morpho_doc2(doc_id)
#    rb.lemmas_freq_doc2(doc_id)
#
# rb.idf_object_features_set(set_id)
# rb.learning_rubric_model(set_id, rubrics_id[0])
#
# for doc_id in set:
#     rb.spot_doc_rubrics2(doc_id, {rubrics_id[0]: None})