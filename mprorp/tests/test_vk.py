import unittest
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from mprorp.crawler.vk import vk_parse_list, vk_parse_item
import os



class SimpleVKTest(unittest.TestCase):

    def test_parse(self):
        path = os.path.dirname(os.path.realpath(__file__))
        dropall_and_create()

        ins_source_url = path + '/test_docs/vk_response.txt'
        #if sys.argv[0][-10:] == 'nosetests3':
        #    ins_source_url = 'mprorp/tests/'+ins_source_url
        #ins_source = Source(url=ins_source_url, name='test source')
        #insert(ins_source)
        #ins_source_id = ins_source.source_id

        s = open(ins_source_url, 'r').read()

        # Do we have all docs?
        session = db_session()
        app_id = "test"
        documents = vk_parse_list(s, app_id, session)
        session.commit()
        doc_ids = []
        for doc in documents:
            doc.app_id = app_id
            doc_ids.append(doc.doc_id)
        print(doc_ids)
        session.close()
        docs = select(Document.doc_id, Document.app_id == app_id).fetchall()
        self.assertEqual(len(docs), 2)

        # Do we have repeated docs?
        session = db_session()
        vk_parse_list(s, app_id, session)
        session.commit()
        session.close()
        docs = select(Document.doc_id, Document.app_id == app_id).fetchall()
        self.assertEqual(len(docs), 2)

        docs = select(Document.doc_id, Document.guid == app_id+'https://vk.com/wall-114326084_4472').fetchall()
        self.assertEqual(len(docs), 1)

        session = db_session()
        for doc_id in doc_ids:
            doc = session.query(Document).filter_by(doc_id=doc_id).first()
            vk_parse_item(doc)
        session.commit()
        session.remove()

        doc_source = select(Document.doc_source, Document.guid == app_id+'https://vk.com/wall-114326084_4472').fetchone()[0]
        print("doc_source", doc_source)
        self.assertEqual(doc_source, 'тест fulltext 4472')

        stripped = select(Document.stripped, Document.guid == app_id+'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(stripped, 'тест fulltext 4472')

        published_date = select(Document.published_date, Document.guid == app_id+'https://vk.com/wall-114326084_4472').fetchone()[0]
        self.assertEqual(str(published_date), '2016-05-30 13:42:22')

        doc_meta = select(Document.meta, Document.guid == app_id+'https://vk.com/wall-114326084_4472').fetchone()[0]
        post_type = doc_meta["vk_post_type"]
        vk_first_attachment_type = doc_meta["vk_attachments"][0]["type"]
        self.assertEqual(post_type, 'post')
        self.assertEqual(vk_first_attachment_type, 'photo')


if __name__ == '__main__':
    unittest.main()


"""
TODO: check owner info
"""