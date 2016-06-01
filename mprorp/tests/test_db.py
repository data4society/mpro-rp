"""database structure and connection tests"""
import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import random
import datetime
import math


class SimpleDBTest(unittest.TestCase):

    def test_db_init(self):
        """drop all and create all tables"""
        dropall_and_create()

    def test_insert_select(self):
        """insert and check insert result"""
        dropall_and_create()

        ins_doc_title = str(random.random())
        ins_doc = Document(title=ins_doc_title, type='article')
        insert(ins_doc)
        ins_doc_id = ins_doc.doc_id

        sel_doc_title = select(Document.title, Document.doc_id == ins_doc_id).fetchone()[0]
        self.assertEqual(ins_doc_title, sel_doc_title)

    def test_update_select(self):
        """update and check update result"""
        dropall_and_create()
        ins_doc = Document(title="title", type='article')
        insert(ins_doc)
        ins_doc_id = ins_doc.doc_id

        upd_doc_title = str(random.random())
        upd_doc = Document(doc_id = ins_doc_id, title = upd_doc_title)
        update(upd_doc)

        sel_doc_title = select(Document.title, Document.doc_id == ins_doc_id).fetchone()[0]
        self.assertEqual(upd_doc_title, sel_doc_title)

    def test_cur_timestamp(self):
        """working with timestamp"""
        dropall_and_create()
        ins_doc = Document(type='article')
        insert(ins_doc)
        ins_doc_id = ins_doc.doc_id

        sel_timestamp = select(Document.created, Document.doc_id == ins_doc_id).fetchone()[0]

        self.assertLess(math.fabs(datetime.datetime.now().timestamp() - sel_timestamp.timestamp()),10)



if __name__ == '__main__':
    unittest.main()
