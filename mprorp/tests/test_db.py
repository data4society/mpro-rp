import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import random
import mprorp.analyzer.rubricator as rb
import mprorp.analyzer.db as db

class SimpleDBTest(unittest.TestCase):
    def test_db_init(self):
        dropall_and_create()

    def test_insert_select(self):
        dropall_and_create()

        ins_doc_title = str(random.random())
        ins_doc = Document(title=ins_doc_title)
        insert(ins_doc)
        ins_doc_id = ins_doc.doc_id

        sel_doc_title = select(Document.title, Document.doc_id == ins_doc_id).fetchone()[0]
        self.assertEqual(ins_doc_title, sel_doc_title)

    def test_update_select(self):
        dropall_and_create()
        ins_doc = Document(title="title")
        insert(ins_doc)
        ins_doc_id = ins_doc.doc_id

        upd_doc_title = str(random.random())
        upd_doc = Document(doc_id = ins_doc_id, title = upd_doc_title)
        update(upd_doc)

        sel_doc_title = select(Document.title, Document.doc_id == ins_doc_id).fetchone()[0]
        self.assertEqual(upd_doc_title, sel_doc_title)

    def test_cur_timestamp(self):
        dropall_and_create()
        ins_doc = Document()
        insert(ins_doc)
        ins_doc_id = ins_doc.doc_id

        sel_timestamp = select(Document.issue_date, Document.doc_id == ins_doc_id).fetchone()[0]
        print(sel_timestamp)
        #self.assertEqual(upd_doc_title, sel_doc_title)



if __name__ == '__main__':
    unittest.main()
