"""theme clasterization"""
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from sqlalchemy.orm import load_only
import datetime

import json

from mprorp.analyzer.pymystem3_w import Mystem

mystem = Mystem()

def words_renew():
    print("hi")
    session = db_session()
    docs = session.query(Document) \
        .filter(Document.created < datetime.datetime.now(), Document.title != None) \
        .options(load_only("title")).all()
    print(len(docs))
    mystem.start()
    for doc in docs:
        print(doc.title)
        title_lemmas = mystem.lemmatize(doc.title)
        # mystem.close()
        print(title_lemmas)
        title_lemmas = [word for word in title_lemmas if len(word.strip()) > 2]
        for word in title_lemmas:
            print(word)
            word_obj = session.query(ThemeWord).filter_by(word=word).first()
            if not word_obj:
                word_obj = ThemeWord(word=word, words=dict(), status=0)
                session.add(word_obj)
                print("NEW")
            words = word_obj.words
            print(word_obj.words)
            print(type(word_obj.words))
            for word1 in title_lemmas:
                if word1 in words:
                    words[word1] += 1
                else:
                    words[word1] = 1
            print(words)
            print(json.dumps(words))
            print(json.dumps(words,ensure_ascii=False).decode('string_escape'))
            print(json.dumps(words,ensure_ascii=False).encode('utf8'))
            print(type(json.dumps(words,ensure_ascii=False)))
            word_obj.words = json.dumps(words,ensure_ascii=False).decode('string_escape')
            word_obj.status = 3
            print(word_obj.words)
            print(word_obj)
        print(title_lemmas)
        break
    session.commit()
    session.remove()

    mystem.close()




if __name__ == "__main__":
    words_renew()