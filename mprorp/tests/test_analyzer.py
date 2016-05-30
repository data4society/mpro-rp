import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import random
import mprorp.analyzer.rubricator as rb
import mprorp.analyzer.db as db

class SimpleDBTest(unittest.TestCase):

    def test_rubricator(self):
        dropall_and_create()

        set = []

        doc_1 = Document(stripped="Письмо Маши Васе")
        insert(doc_1)
        set.append(doc_1.doc_id)

        doc_2 = Document(stripped="Первый документ Пети")
        insert(doc_2)
        set.append(doc_2.doc_id)

        doc_3 = Document(stripped="Первое письмо Маши")
        insert(doc_3)
        set.append(doc_3.doc_id)

        doc_4 = Document(stripped="Второй документ Маши")
        insert(doc_4)
        set.append(doc_4.doc_id)

        doc_5 = Document(stripped="Первый документ Васи")
        insert(doc_5)
        set.append(doc_5.doc_id)

        doc_6 = Document(stripped="Второй документ Пети")
        insert(doc_6)
        set.append(doc_6.doc_id)

        doc_7 = Document(stripped="Первое письмо Пети")
        insert(doc_7)
        set.append(doc_7.doc_id)

        doc_8 = Document(stripped="Первое письмо Васи")
        insert(doc_8)
        set.append(doc_8.doc_id)

        doc_9 = Document(stripped="Первый документ Маши")
        insert(doc_9)
        set.append(doc_9.doc_id)

        doc_10 = Document(stripped="Письмо Маши Пете")
        insert(doc_10)
        set.append(doc_10.doc_id)

        new_rubrics = Rubric(name="Маша")
        insert(new_rubrics)
        rubrics_id = new_rubrics.rubric_id

        insert(DocumentRubric(doc_id=set[0], rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=set[2], rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=set[3], rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=set[8], rubric_id=rubrics_id))
        insert(DocumentRubric(doc_id=set[9], rubric_id=rubrics_id))

        for doc_id in set:
            rb.morpho_doc(doc_id)
            rb.lemmas_freq_doc(doc_id)

        set_id = db.put_training_set(set)
        rb.idf_object_features_set(set_id)
        rb.learning_rubric_model(set_id, rubrics_id)

        for doc_id in set:
            rb.spot_doc_rubrics(doc_id, {rubrics_id: None})

        compareAnswers = rb.compare_answers(db.get_model(rubrics_id, set_id)["model_id"], set_id, rubrics_id)
        print(compareAnswers)