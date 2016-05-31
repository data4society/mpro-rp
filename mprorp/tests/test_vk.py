import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.crawler.vk import vk_parse_list
import json


class SimpleVKTest(unittest.TestCase):

    def test_insert_select(self):
        dropall_and_create()

        ins_source_url = 'test_docs/vk_response.txt'
        if sys.argv[0][-10:] == 'nosetests3':
            ins_source_url = 'mprorp/tests/'+ins_source_url
        ins_source = Source(url=ins_source_url, name='test source')
        insert(ins_source)
        ins_source_id = ins_source.source_id

        s = open(ins_source_url, 'r').read()

        # Do we have all docs?
        vk_parse_list(s, ins_source_id)
        docs = select(Document.doc_id, Document.source_ref == ins_source_id).fetchall()
        self.assertEqual(len(docs), 2)

        # Do we have repeated docs?
        vk_parse_list(s, ins_source_id)
        docs = select(Document.doc_id, Document.source_ref == ins_source_id).fetchall()
        self.assertEqual(len(docs), 2)

        docs = select(Document.doc_id, Document.guid == 'https://vk.com/wall-114326084_4472').fetchall()
        self.assertEqual(len(docs), 1)

        doc_source = select(Document.doc_source, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(doc_source, 'тест fulltext 4472')

        stripped = select(Document.stripped, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(stripped, 'тест fulltext 4472')

        created_time = select(Document.created, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(str(created_time), '2016-05-30 13:42:22')

        doc_meta = select(Document.meta, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        doc_meta = json.loads(doc_meta)
        post_type = doc_meta["vk_post_type"]
        vk_first_attachment_type = doc_meta["vk_attachments"][0]["type"]
        self.assertEqual(post_type, 'post')
        self.assertEqual(vk_first_attachment_type, 'photo')


if __name__ == '__main__':
    unittest.main()