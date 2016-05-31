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

    def test_lemmas_freq(self):
        # morpho analysis
        dropall_and_create()
        my_doc = Document(stripped='Эти типы стали есть на складе')
        insert(my_doc)
        doc_id = str(my_doc.doc_id)
        rb.morpho_doc(doc_id)
        rb.lemmas_freq_doc(doc_id)
        lemmas = db.get_lemmas(doc_id)
        self.assertEqual(lemmas['склад'], 1)

    def test_training_set_idf(self):

        set_id, rubric_id = fill_db()
        rb.idf_object_features_set(set_id)
        # check we can overwrite idf:
        rb.idf_object_features_set(set_id)
        result = select(ObjectFeatures.doc_id, ObjectFeatures.set_id == set_id).fetchall()
        self.assertEqual(len(result), 10)

    def test_model(self):

        set_id, rubric_id = fill_db()
        rb.idf_object_features_set(set_id)
        rb.learning_rubric_model(set_id, rubric_id)
        model = db.get_model(rubric_id, set_id)
        self.assertEqual(model['features_num'], 11)

    def test_rubricator(self):

        set_id, rubrics_id = fill_db()

        rb.idf_object_features_set(set_id)
        rb.learning_rubric_model(set_id, rubrics_id)

        for doc_id in db.get_set_docs(set_id):
            rb.spot_doc_rubrics(doc_id, {rubrics_id: None})
            # check we can overwrite rubricationresults:
            rb.spot_doc_rubrics(doc_id, {rubrics_id: None})

        result = rb.f1_score(db.get_model(rubrics_id, set_id)["model_id"], set_id, rubrics_id)
        # self.assertEqual(result['true_negative'], 5)
        # self.assertEqual(result['true_positive'], 5)
        self.assertEqual(result['f1'], 1)


def fill_db():

    docs = ["Письмо Маши Васе",
            "Первый документ Пети",
            "Первое письмо Маши",
            "Второй документ Маши",
            "Первый документ Васи",
            "Второй документ Пети",
            "Первое письмо Пети",
            "Первое письмо Васи",
            "Первый документ Маши",
            "Письмо Маши Пете"]
    answers = [1, 0, 1, 0, 0, 0, 1, 1, 0, 1]

    tr_set = []

    for doc in docs:
        doc_db = Document(stripped=doc)
        insert(doc_db)
        tr_set.append(doc_db.doc_id)

    new_rubric = Rubric(name="Маша")
    insert(new_rubric)
    rubric_id = str(new_rubric.rubric_id)

    for i in range(10):
        if answers[i]:
            insert(DocumentRubric(doc_id=str(tr_set[i]), rubric_id=rubric_id))

    for doc_id in tr_set:
        rb.morpho_doc(str(doc_id))
        rb.lemmas_freq_doc(str(doc_id))

    set_id = str(db.put_training_set(tr_set))

    return set_id, rubric_id
