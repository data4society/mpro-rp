import db.dbDriver
from db.models import *
from sqlalchemy.orm import load_only
import random

class start:

    if __name__ == "__main__":
        dbase = db.dbDriver.dbDriver.engine
        print(dbase)

        session = db.dbDriver.dbDriver.DBSession()

        # Insert a user in the User table
        new_user = User()
        session.add(new_user)
        session.commit()

        new_source_type = SourceType(name="vk")
        session.add(new_source_type)
        session.commit()


        # Insert a doc in the Document table with reference to user
        new_doc = Document(validated_by = new_user, doc_source = "test")
        session.add(new_doc)
        session.commit()

        #Get all documents
        docs = session.query(Document).all()
        #Get id of first document
        print(docs[0].doc_id)
        #or:
        print(session.query(Document).first().doc_id)

        #doc_source property of some document
        print(session.query(Document).filter(Document.doc_id == "7a074073-7747-47b9-aba0-1f5990ddbaf9").one().doc_source)
        #same with not full object
        print(session.query(Document).options(load_only(Document.doc_source)).filter(Document.doc_id == "7a074073-7747-47b9-aba0-1f5990ddbaf9").one().doc_source)

        #Update document object
        some_doc = session.query(Document).filter(Document.doc_id == "7a074073-7747-47b9-aba0-1f5990ddbaf9").one()
        print(some_doc.doc_source)
        some_doc.doc_source = random.random()
        session.commit()
        #check update:
        some_doc = session.query(Document).filter(Document.doc_id == "7a074073-7747-47b9-aba0-1f5990ddbaf9").one()
        print(some_doc.doc_source)

