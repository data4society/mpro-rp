"""theme clasterization"""
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from sqlalchemy.orm import load_only
import datetime

import json

from mprorp.analyzer.pymystem3_w import Mystem
from sqlalchemy.orm.attributes import flag_modified

WORD_MIN_MENTIONS = 30
WORD_GOOD_THRESHOLD = 0.68

mystem = Mystem()

def words_renew():
    print("hi")
    session = db_session()
    now_time = datetime.datetime.now()
    docs = session.query(Document) \
        .filter(Document.created < datetime.datetime.now(), Document.title != None) \
        .options(load_only("title")).all()
    print(len(docs))
    mystem.start()
    objects = dict()
    i = 0
    last_theme_words_renew = Variable(name="last_theme_words_renew",json=dict())
    session.add(last_theme_words_renew)
    time = datetime.datetime.now()
    last_theme_words_renew.json["value"] = str(time)
    flag_modified(last_theme_words_renew, "json")
    for doc in docs:
        #print(doc.title)
        title_lemmas = mystem.lemmatize(doc.title)
        # mystem.close()
        #print(title_lemmas)
        title_lemmas = [word for word in title_lemmas if len(word.strip()) > 2]
        for word in title_lemmas:
            #print(word)
            if word not in objects:
                word_obj = session.query(ThemeWord).filter_by(word=word).first()
                if not word_obj:
                    word_obj = ThemeWord(word=word, words=dict(), status=0)
                    session.add(word_obj)
                    #print("NEW")
                objects[word] = word_obj
            else:
                word_obj = objects[word]
            words = word_obj.words
            for word1 in title_lemmas:
                if word1 in words:
                    words[word1] += 1
                else:
                    words[word1] = 1

            word_obj.words = words
            flag_modified(word_obj, "words")
        i+=1
        print(i)
        #if i == 10:
        #    break
    for word in objects:
        word_obj = objects[word]
        words = word_obj.words
        #print(words)
        #print(words.values())
        #print(list(words.values()))
        word_nums = list(words.values())
        word_nums.sort(reverse=True)
        #print(word_nums)
        word_same = word_nums[0]
        #for word_num in word_nums:
        if word_same < WORD_MIN_MENTIONS:
            word_obj.status = 0
        else:
            word_nums = word_nums[1:5]
            #print(word_nums)
            if sum(word_nums)/word_same > WORD_GOOD_THRESHOLD:
                word_obj.status = 1
            else:
                word_obj.status = -1
        #break
    session.commit()
    session.remove()
    mystem.close()


def check_middle():
    session = db_session()
    objects = session.query(ThemeWord).all()
    s = 0
    for word_obj in objects:
        word = word_obj.word
        words = word_obj.words
        #if word_same >= WORD_MIN_MENTIONS:
        #    sum+=1
        #if word_obj.status == -1:
        #    print(word)

        word_nums = list(words.values())
        word_nums.sort(reverse=True)
        #print(word_nums)
        word_same = word_nums[0]
        # for word_num in word_nums:
        if word_same < WORD_MIN_MENTIONS:
            word_obj.status = 0
        else:
            s += 1
            word_nums = word_nums[1:5]
            if sum(word_nums) / word_same > WORD_GOOD_THRESHOLD:
                word_obj.status = 1
            else:
                word_obj.status = -1
    print(s)
    session.commit()
    session.remove()


if __name__ == "__main__":
    check_middle()
    #words_renew()