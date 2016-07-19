import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.crawler.vk import vk_parse_list
import os



class SimpleVKTest(unittest.TestCase):

    def test_parse(self):
        path = os.path.dirname(os.path.realpath(__file__))
        dropall_and_create()

        ins_source_url = path + '/test_docs/vk_response.txt'
        #if sys.argv[0][-10:] == 'nosetests3':
        #    ins_source_url = 'mprorp/tests/'+ins_source_url
        ins_source = Source(url=ins_source_url, name='test source')
        insert(ins_source)
        ins_source_id = ins_source.source_id

        s = open(ins_source_url, 'r').read()

        # Do we have all docs?
        session = DBSession()
        vk_parse_list(s, ins_source_id, session)
        session.commit()
        session.close()
        docs = select(Document.doc_id, Document.source_id == ins_source_id).fetchall()
        self.assertEqual(len(docs), 2)

        # Do we have repeated docs?
        session = DBSession()
        vk_parse_list(s, ins_source_id, session)
        session.commit()
        session.close()
        docs = select(Document.doc_id, Document.source_id == ins_source_id).fetchall()
        self.assertEqual(len(docs), 2)

        docs = select(Document.doc_id, Document.guid == 'https://vk.com/wall-114326084_4472').fetchall()
        self.assertEqual(len(docs), 1)

        doc_source = select(Document.doc_source, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(doc_source, 'тест fulltext 4472')

        stripped = select(Document.stripped, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(stripped, 'тест fulltext 4472')

        published_date = select(Document.published_date, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(str(published_date), '2016-05-30 13:42:22')

        doc_meta = select(Document.meta, Document.guid == 'https://vk.com/wall-114326084_4472').fetchone()[0]
        post_type = doc_meta["vk_post_type"]
        vk_first_attachment_type = doc_meta["vk_attachments"][0]["type"]
        self.assertEqual(post_type, 'post')
        self.assertEqual(vk_first_attachment_type, 'photo')


if __name__ == '__main__':
    unittest.main()


"""
TODO: check owner info
"""