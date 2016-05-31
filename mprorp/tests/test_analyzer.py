import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import mprorp.analyzer.rubricator as rb
import mprorp.analyzer.db as db


class SimpleDBTest(unittest.TestCase):

    def test_morpho(self):
        # morpho analysis
        dropall_and_create()
        my_doc = Document(stripped='Эти типы стали есть на складе')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc(doc_id)
        morpho = db.get_morpho(doc_id)
        self.assertEqual(morpho[0]['text'], 'Эти')


    def test_rubricator(self):
        # insert 10 simple documents in db and form training set
        # learn model for 1 rubric
        # spot rubric for documents from same set
        dropall_and_create()

        tr_set = []

        doc_1 = Document(stripped="Письмо Маши Васе")
        insert(doc_1)
        tr_set.append(doc_1.doc_id)

        doc_2 = Document(stripped="Первый документ Пети")
        insert(doc_2)
        tr_set.append(doc_2.doc_id)

        doc_3 = Document(stripped="Первое письмо Маши")
        insert(doc_3)
        tr_set.append(doc_3.doc_id)

        doc_4 = Document(stripped="Второй документ Маши")
        insert(doc_4)
        tr_set.append(doc_4.doc_id)

        doc_5 = Document(stripped="Первый документ Васи")
        insert(doc_5)
        tr_set.append(doc_5.doc_id)

        doc_6 = Document(stripped="Второй документ Пети")
        insert(doc_6)
        tr_set.append(doc_6.doc_id)

        doc_7 = Document(stripped="Первое письмо Пети")
        insert(doc_7)
        tr_set.append(doc_7.doc_id)

        doc_8 = Document(stripped="Первое письмо Васи")
        insert(doc_8)
        tr_set.append(doc_8.doc_id)

        doc_9 = Document(stripped="Первый документ Маши")
        insert(doc_9)
        tr_set.append(doc_9.doc_id)

        doc_10 = Document(stripped="Письмо Маши Пете")
        insert(doc_10)
        tr_set.append(doc_10.doc_id)

        new_rubrics = Rubric(name="Маша")
        insert(new_rubrics)
        rubrics_id = str(new_rubrics.rubric_id)

        insert(DocumentRubric(doc_id=str(tr_set[0]), rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=str(tr_set[2]), rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=str(tr_set[3]), rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=str(tr_set[8]), rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=str(tr_set[9]), rubric_id=rubrics_id))

        for doc_id in tr_set:
            rb.morpho_doc(doc_id)
            rb.lemmas_freq_doc(doc_id)

        set_id = str(db.put_training_set(tr_set))
        rb.idf_object_features_set(set_id)
        rb.learning_rubric_model(set_id, rubrics_id)

        for doc_id in tr_set:
            rb.spot_doc_rubrics(doc_id, {rubrics_id: None})

        result = rb.compare_answers(db.get_model(rubrics_id, set_id)["model_id"], set_id, rubrics_id)
        print(result)