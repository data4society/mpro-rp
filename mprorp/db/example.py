"""examples for working with database driver"""
from mprorp.db.dbDriver import *
from mprorp.db.models import *
import random

if __name__ == "__main__":
    # INSERT (ORM)
    new_user = User()
    insert(new_user)
    print(new_user.user_id)

    # SELECT (query)
    #print(select(Document.doc_source,Document.doc_id == '7a074073-7747-47b9-aba0-1f5990ddbaf9').fetchone()[0])

    print(select(TrainingSet.doc_num,TrainingSet.set_id == '41a77748-3047-4cb0-abc1-204607ae86ed').fetchone()[0])
    print(select([TrainingSet.doc_num, TrainingSet.set_name], TrainingSet.set_id == '41a77748-3047-4cb0-abc1-204607ae86ed').fetchall()[0])

    # UPDATE (ORM)
    update(Document(doc_id='7a074073-7747-47b9-aba0-1f5990ddbaf9',doc_source=random.random()))
    print(select(Document.doc_source,Document.doc_id == '7a074073-7747-47b9-aba0-1f5990ddbaf9').fetchone()[0])
