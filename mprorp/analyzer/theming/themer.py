"""theme clasterization"""
from mprorp.db.dbDriver import *
from mprorp.db.models import *
from sqlalchemy.orm import load_only
import datetime

import json
import math

from mprorp.analyzer.pymystem3_w import Mystem
from sqlalchemy.orm.attributes import flag_modified
#import pymorphy2

WORD_MIN_MENTIONS = 30
WORD_GOOD_THRESHOLD = 0.68
MAX_THEME_PAUSE = 3*24*3600
THEME_THRESHOLD = 0.2

mystem = Mystem()

def words_renew():
    print("hi")
    session = db_session()
    now_time = datetime.datetime.now()
    last_theme_words_renew = session.query(Variable) \
        .filter(Variable.name=="last_theme_words_renew") \
        .first()
    docs = session.query(Document) \
        .filter(Document.created > last_theme_words_renew.json["value"], Document.title != None) \
        .options(load_only("title")).all()
    mystem.start()
    objects = dict()
    i = 0
    #last_theme_words_renew = Variable(name="last_theme_words_renew",json=dict())
    #session.add(last_theme_words_renew)
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


def reg_theming_0(doc, session):
    #now_time = datetime.datetime.now()
    #print("AAA",session.query(Theme).count())
    #print(doc.title)
    #print(doc.lemmas)
    themes = session.query(Theme) \
        .filter(Theme.last_renew_time > datetime.datetime.fromtimestamp(doc.created.timestamp()-MAX_THEME_PAUSE)) \
        .all()
    #print(len(themes))
    #print("BBB")
    bad_words = session.query(ThemeWord.word).filter(ThemeWord.status == -1).all()
    bad_words = [bad_word for (bad_word,) in bad_words]
    #print(bad_words)
    #print(bad_words[0])
    #print(type(bad_words[0]))
    #print(len(bad_words))
    #mystem.start()
    title_lemmas = mystem.lemmatize(doc.title)
    #print(title_lemmas)
    title_lemmas = [word for word in title_lemmas if len(word.strip()) > 2]
    title_lemmas = [word for word in title_lemmas if word not in bad_words]
    title_len = len(title_lemmas)
    title_len_sqrt = math.sqrt(title_len)
    #print(title_lemmas)
    best_theme = 0
    best_reit = 0
    good_themes = []
    good_themes_ids = []
    for theme in themes:
        reit = 0
        theme_words = theme.words
        #print(theme.title)
        #print(theme_words)
        for word in title_lemmas:
            if word in theme_words:
                reit += theme_words[word]/title_len_sqrt
        #print(reit)
        if reit >= THEME_THRESHOLD:
            good_themes_ids.append(str(theme.theme_id))
            good_themes.append(theme)
            #print("GOOD")
            if reit > best_reit:
                best_reit = reit
                best_theme = theme
                #print("BEST")
    docs_in_theme_num = 1
    theme_words_arr = []
    if len(good_themes) > 0:
        best_theme_words = dict()
        for theme in good_themes:
            num = session.query(Document).filter_by(theme_id=theme.theme_id).count()
            docs_in_theme_num += num
            theme_words = theme.words
            theme_words_arr.append(theme_words)
            #print("!!!", theme_words)
            for word in theme_words:
                theme_words[word] *= num
            if theme.theme_id != best_theme.theme_id:
                session.delete(theme)
                #("DELETE")
        for theme_words in theme_words_arr:
            for word in theme_words:
                if word not in best_theme_words:
                    best_theme_words[word] = 0
                best_theme_words[word] += theme_words[word]/docs_in_theme_num
        if len(good_themes) > 1:
            good_themes_ids.remove(str(best_theme.theme_id))
            for d in session.query(Document).filter(Document.theme_id.in_(good_themes_ids)).all():
                d.theme = best_theme

    else:
        best_theme = Theme(words=dict())
        session.add(best_theme)
        best_theme_words = best_theme.words
    #print(best_reit)
    """
    if best_reit < THEME_THRESHOLD:
        best_theme = Theme(words=dict())
        session.add(best_theme)
        best_theme_words = best_theme.words
    else:
        print(best_theme.title)
        docs_in_theme_num = session.query(Document).filter_by(theme_id=best_theme.theme_id).count()+1
        best_theme_words = best_theme.words
        for word in best_theme_words:
            best_theme_words[word] = best_theme_words[word]*(docs_in_theme_num-1)/docs_in_theme_num
    """
    for word in title_lemmas:
        if word not in best_theme_words:
            best_theme_words[word] = 0
        best_theme_words[word] += 1/(title_len_sqrt*docs_in_theme_num)
    best_theme_words_sum = 0
    for word in best_theme_words:
        best_theme_words_sum += best_theme_words[word]*best_theme_words[word]
    best_theme_words_sum = math.sqrt(best_theme_words_sum)
    for word in best_theme_words:
        best_theme_words[word] = best_theme_words[word]/best_theme_words_sum
    best_theme.title = doc.title
    best_theme.last_renew_time = doc.created
    best_theme.words = best_theme_words
    flag_modified(best_theme, "words")
    doc.theme = best_theme
    #print(best_theme.words)
#   for theme in themes:

    #mystem.close()
    #exit()


def reg_theming_1(doc, session):
    #now_time = datetime.datetime.now()
    print("AAA",session.query(Theme).count())
    print(doc.title)
    #print(doc.lemmas)
    themes = session.query(Theme) \
        .filter(Theme.last_renew_time > datetime.datetime.fromtimestamp(doc.created.timestamp()-MAX_THEME_PAUSE)) \
        .all()
    #print(len(themes))
    #print("BBB")
    bad_words = session.query(ThemeWord.word).filter(ThemeWord.status == -1).all()
    bad_words = [bad_word for (bad_word,) in bad_words]
    #print(bad_words)
    #print(bad_words[0])
    #print(type(bad_words[0]))
    #print(len(bad_words))
    #mystem.start()
    title_lemmas = mystem.lemmatize(doc.title)
    #print(title_lemmas)
    title_lemmas = [word for word in title_lemmas if len(word.strip()) > 2]
    title_lemmas = [word for word in title_lemmas if word not in bad_words]
    title_len = len(title_lemmas)
    title_len_sqrt = math.sqrt(title_len)
    print(title_lemmas)
    print(title_len_sqrt)
    best_theme = 0
    best_reit = 0
    good_themes = []
    good_themes_ids = []
    for theme in themes:
        theme_words_arr = theme.words
        print(theme.title)
        print(theme_words_arr)
        for theme_words in theme_words_arr:
            reit = 0
            for word in title_lemmas:
                if word in theme_words:
                    reit += theme_words[word]/title_len_sqrt
            print(reit)
            if reit >= THEME_THRESHOLD:
                good_themes_ids.append(str(theme.theme_id))
                good_themes.append(theme)
                print("GOOD")
                if reit > best_reit:
                    best_reit = reit
                    best_theme = theme
                    print("BEST")
                break
    docs_in_theme_num = 1
    theme_words_arr = []
    if len(good_themes) > 0:
        for theme in good_themes:
            num = session.query(Document).filter_by(theme_id=theme.theme_id).count()
            docs_in_theme_num += num
            theme_words = theme.words
            theme_words_arr.extend(theme_words)
            #print("!!!", theme_words)
            if theme.theme_id != best_theme.theme_id:
                session.delete(theme)
                #("DELETE")
        if len(good_themes) > 1:
            good_themes_ids.remove(str(best_theme.theme_id))
            for d in session.query(Document).filter(Document.theme_id.in_(good_themes_ids)).all():
                d.theme = best_theme

    else:
        best_theme = Theme()
        session.add(best_theme)
    best_theme_words = dict()
    #print(best_reit)
    for word in title_lemmas:
        best_theme_words[word] = 1/title_len_sqrt
    theme_words_arr.append(best_theme_words)
    best_theme.title = doc.title
    best_theme.last_renew_time = doc.created
    best_theme.words = theme_words_arr
    flag_modified(best_theme, "words")
    doc.theme = best_theme
    print(best_theme.words)
#   for theme in themes:

    #mystem.close()
    #exit()



def reg_theming(doc, session):
    #now_time = datetime.datetime.now()
    print("AAA",session.query(Theme).count())
    print(doc.title)
    #print(doc.lemmas)
    themes = session.query(Theme) \
        .filter(Theme.last_renew_time > datetime.datetime.fromtimestamp(doc.created.timestamp()-MAX_THEME_PAUSE)) \
        .all()
    #print(len(themes))
    #print("BBB")
    bad_words = session.query(ThemeWord.word).filter(ThemeWord.status == -1).all()
    bad_words = [bad_word for (bad_word,) in bad_words]
    #print(bad_words)
    #print(bad_words[0])
    #print(type(bad_words[0]))
    #print(len(bad_words))
    #mystem.start()
    title_lemmas = mystem.lemmatize(doc.title)
    #print(title_lemmas)
    title_lemmas = [word for word in title_lemmas if len(word.strip()) > 2]
    title_lemmas = [word for word in title_lemmas if word not in bad_words]
    title_len = len(title_lemmas)
    title_len_sqrt = math.sqrt(title_len)
    print(title_lemmas)
    print(title_len_sqrt)
    best_theme = 0
    best_reit = 0
    good_themes = []
    good_themes_ids = []
    for theme in themes:
        theme_words_arr = theme.words
        print(theme.title)
        print(theme_words_arr)
        reit_mid = 0
        for theme_words in theme_words_arr:
            reit = 0
            for word in title_lemmas:
                if word in theme_words:
                    reit += theme_words[word]/title_len_sqrt
            print(reit)
            reit_mid += reit
        reit_mid = reit_mid/len(theme_words_arr)
        print(reit_mid)
        if reit_mid >= THEME_THRESHOLD:
            good_themes_ids.append(str(theme.theme_id))
            good_themes.append(theme)
            print("GOOD")
            if reit_mid > best_reit:
                best_reit = reit_mid
                best_theme = theme
                print("BEST")
    docs_in_theme_num = 1
    theme_words_arr = []
    if len(good_themes) > 0:
        for theme in good_themes:
            num = session.query(Document).filter_by(theme_id=theme.theme_id).count()
            docs_in_theme_num += num
            theme_words = theme.words
            theme_words_arr.extend(theme_words)
            #print("!!!", theme_words)
            if theme.theme_id != best_theme.theme_id:
                session.delete(theme)
                #("DELETE")
        if len(good_themes) > 1:
            good_themes_ids.remove(str(best_theme.theme_id))
            for d in session.query(Document).filter(Document.theme_id.in_(good_themes_ids)).all():
                d.theme = best_theme

    else:
        best_theme = Theme()
        session.add(best_theme)
    best_theme_words = dict()
    #print(best_reit)
    for word in title_lemmas:
        best_theme_words[word] = 1/title_len_sqrt
    theme_words_arr.append(best_theme_words)
    best_theme.title = doc.title
    best_theme.last_renew_time = doc.created
    best_theme.words = theme_words_arr
    flag_modified(best_theme, "words")
    doc.theme = best_theme
    print(best_theme.words)
#   for theme in themes:

    #mystem.close()
    #exit()


def print_by_themes():
    session = db_session()
    themes = session.query(Theme).options(load_only("theme_id")).all()
    i = 0
    for theme in themes:
        i+=1
        print(i)
        docs = session.query(Document).options(load_only("title")).filter(Document.theme_id == theme.theme_id).order_by(Document.created).all()
        for doc_obj in docs:
            print(doc_obj.title)

    session.remove()


def mass_themization():
    mystem.start()
    session = db_session()
    docs = session.query(Document).options(load_only("doc_id")). \
        join(Source, Source.source_id == Document.source_id).filter(Document.status == 1001, Document.theme_id == None,
                                                                    Source.source_type_id == '1d6210b2-5ff3-401c-b0ba-892d43e0b741'). \
        order_by(Document.created).all()
    i = 0
    session.remove()
    for doc_obj in docs:
        session = db_session()
        doc = session.query(Document).filter_by(doc_id=doc_obj.doc_id).first()
        get_main_words(doc.title, doc.lemmas, session)
        exit()
        reg_theming_0(doc, session)
        session.commit()
        # print(doc.theme_id)
        session.remove()
        i += 1
        print(i)
        if i == 350:
            break

    docs = session.query(Document).options(load_only("theme_id")). \
        join(Source, Source.source_id == Document.source_id).filter(Document.status == 1001,
                                                                    Source.source_type_id == '1d6210b2-5ff3-401c-b0ba-892d43e0b741'). \
        order_by(Document.created).all()

    print(len(docs))
    for doc_obj in docs:
        print(doc_obj.theme_id)
    # exit()

    # print(docs)
    # doc.status = new_status
    # session.commit()
    mystem.close()
    # router(doc.doc_id, new_status)
    # doc = session.query(Document).filter_by(doc_id="8c429c1a-54c6-4256-81ba-5db619032937").first()
    # reg_theming(doc, session)
    print_by_themes()


def compute_idfs():
    session = db_session()
    docs = session.query(Document).options(load_only("doc_id")). \
        join(Source, Source.source_id == Document.source_id).filter(Document.status == 1001,
                                                                    Source.source_type_id == '1d6210b2-5ff3-401c-b0ba-892d43e0b741'). \
        order_by(Document.created).all()
    i = 0
    session.remove()
    words = dict()
    docs_len = len(docs)
    # print("docs_num:", docs_len)
    for doc_obj in docs:
        session = db_session()
        words_in_doc = dict()

        doc = session.query(Document).options(load_only("morpho")).filter_by(doc_id=doc_obj.doc_id).first()
        for obj in doc.morpho:
            if 'analysis' in obj:
                for analys in obj['analysis']:
                    word = analys['lex']
                    if word not in words_in_doc:
                        words_in_doc[word] = list()
                    words_in_doc[word].append(analys['wt'])
        for word in words_in_doc:
            p = 1
            for pi in words_in_doc[word]:
                p *= 1-pi
            words_in_doc[word] = 1-p

        #doc = session.query(Document).options(load_only("lemmas")).filter_by(doc_id=doc_obj.doc_id).first()
        #for word in doc.lemmas:
        #    words_in_doc[word] = 1
        for word in words_in_doc:
            if word not in words:
                words[word] = words_in_doc[word]
            else:
                words[word] += words_in_doc[word]
        session.remove()
        i += 1
        print(i)

    session = db_session()
    print("words num:",len(words))
    docs_len += 1
    for word in words:
        num = words[word]
        idf = IDF(word=word, num=num  #, idf=math.log(docs_len/num,2)
        )
        session.add(idf)
        session.commit()
    print("complete!")


def get_main_words(title, lemmas, session):
    mains = dict()
    words_len = len(lemmas)
    docs_len = variable_get("idf_corpus_count",2500)
    for word in lemmas:
        if word in mains:
            mains[word] += 1
        else:
            mains[word] = 1

    #for word in mains:
    #    mains[word] = mains[word]/words_len
    print(mains.items())
    print(type(mains.items()))
    mains = {k: v/words_len for k, v in mains.items()}  #tf
    words_list = list(mains.keys())
    idf_objs = session.query(IDF).options(load_only("word","idf")).filter(IDF.word.in_(words_list)).all()
    idf_dict = dict()
    for idf_obj in idf_objs:
        idf_dict[idf_obj.word] = idf_obj.idf

    for word in mains:
        if word in idf_dict:
            mains[word] = mains[word]*idf_dict[word]
        else:
            mains[word] = math.log(docs_len+1,2)
    print(sorted(mains.items()))
    print(sorted(mains.items(), key=lambda tup: tup[1], reverse=True))
    mains = {k: v for k, v in sorted(mains.items(), key=lambda tup: tup[1], reverse=True)[:5]}
    print(mains)


if __name__ == "__main__":
    compute_idfs()
    #check_middle()
    #words_renew()
    #print_by_themes()
    #exit()
    #compute_idfs()
    #exit()
    """
    morph = pymorphy2.MorphAnalyzer()
    print(morph)
    print(morph.parse("справедливо"))
    print(morph.parse("российский")[0].normal_form)
    print(morph.parse("конский")[0].normal_form)
    print(morph.parse("правящий")[0].normal_form)
    print(morph.parse("Александрам")[0].normal_form)
    print(morph.parse("думающий")[0].normal_form)
    exit()
    """
    mass_themization()

"""
многопоточность тут явно может наносить определенный вред
"""